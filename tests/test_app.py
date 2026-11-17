import os, tempfile
import pytest
from fastapi.testclient import TestClient

os.environ["CACHE_DB"] = os.path.join(tempfile.mkdtemp(), "t.sqlite3")
os.environ["RATE_LIMIT_PER_HOUR"] = "3"

from app.main import app            # noqa: E402
from app import coach, cache        # noqa: E402

GOOD = {
    "core_idea": "c", "why_it_works": "w",
    "worked_example": {"problem": "p", "steps": ["a", "b"], "answer": "x"},
    "misconceptions": [{"mistake": "m", "why_students_think_it": "w", "how_to_respond": "h"}] * 3,
    "lesson_ideas": ["1", "2", "3"], "differentiation": {"simpler": "s", "extension": "e"}, "activity": "act",
}
calls = {"n": 0}


@pytest.fixture(autouse=True)
def fake_llm(monkeypatch):
    calls["n"] = 0
    cache._hits.clear()
    async def fake(system, user):
        calls["n"] += 1
        return GOOD
    monkeypatch.setattr(coach, "complete_json", fake)


client = TestClient(app)


def test_returns_card_and_grounds_on_vetted_lesson():
    r = client.post("/coach", json={"topic": "dividing fractions", "grade": "Grade 6"})
    assert r.status_code == 200
    assert r.json()["source"] == "vetted_lesson"


def test_unknown_topic_is_flagged_ai_only():
    r = client.post("/coach", json={"topic": "topology of knots", "grade": "Grade 12"})
    assert r.json()["source"] == "ai_only"


def test_second_identical_request_uses_cache_not_llm():
    client.post("/coach", json={"topic": "Cache Me", "grade": "Grade 7"})
    r = client.post("/coach", json={"topic": "  cache   me ", "grade": "Grade 7"})
    assert r.json()["cached"] is True and calls["n"] == 1


def test_rejects_bad_input():
    assert client.post("/coach", json={"topic": "x" * 500}).status_code == 422
    assert client.post("/coach", json={"topic": "ok topic", "grade": "Grade 99"}).status_code == 422


def test_rate_limit_only_on_uncached():
    for i in range(3):
        assert client.post("/coach", json={"topic": f"topic number {i}"}).status_code == 200
    assert client.post("/coach", json={"topic": "one more topic"}).status_code == 429
    assert client.post("/coach", json={"topic": "topic number 0"}).status_code == 200  # cached still fine


def test_bad_model_output_gives_safe_error(monkeypatch):
    async def bad(system, user):
        return {"nonsense": True}
    monkeypatch.setattr(coach, "complete_json", bad)
    r = client.post("/coach", json={"topic": "broken output"})
    assert r.status_code == 502 and "nonsense" not in r.text
