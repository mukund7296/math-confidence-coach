"""Tiny keyword retrieval over hand-written/open lessons in /lessons.
Deliberately simple: 3 lessons don't need a vector DB. Swap for embeddings when the corpus grows."""
import re
from pathlib import Path

LESSON_DIR = Path(__file__).resolve().parent.parent / "lessons"


def _tokens(s: str) -> set[str]:
    return set(re.findall(r"[a-z]{3,}", s.lower()))


def load_lessons() -> list[dict]:
    out = []
    for p in sorted(LESSON_DIR.glob("*.md")):
        text = p.read_text(encoding="utf-8")
        lines = text.splitlines()
        title = lines[0].lstrip("# ").strip()
        kw = lines[1].replace("keywords:", "").strip() if len(lines) > 1 else ""
        out.append({"title": title, "keywords": _tokens(kw + " " + title), "text": text})
    return out


def find_lesson(topic: str) -> dict | None:
    t = _tokens(topic)
    best, best_score = None, 0
    for lesson in load_lessons():
        score = len(t & lesson["keywords"])
        if score > best_score:
            best, best_score = lesson, score
    return best
