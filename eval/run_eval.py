"""Quality gate. Run: python -m eval.run_eval   (needs a real LLM key; costs a few cents)
Automatic checks: valid structure, required concepts present, banned test/score language absent.
Then prints each worked example so a human (ideally a real maths teacher) can verify the maths in ~5 min.
Automatic checks catch format and tone failures; only a human can fully confirm correctness."""
import asyncio, json, pathlib, re, sys
from dotenv import load_dotenv
load_dotenv()
from app.coach import make_card
from app.schema import CoachRequest

BANNED = re.compile(r"\b(quiz|test yourself|exam|certificate|your score|grade yourself)\b", re.I)


async def main() -> int:
    cases = json.loads((pathlib.Path(__file__).parent / "cases.json").read_text())
    failures = 0
    for c in cases:
        res = await make_card(CoachRequest(topic=c["topic"], grade=c["grade"]))
        blob = res.card.model_dump_json().lower()
        problems = [f"missing '{w}'" for w in c["must_contain"] if w not in blob]
        if BANNED.search(blob):
            problems.append("contains test/score language")
        failures += bool(problems)
        print(f"\n[{'FAIL' if problems else 'PASS'}] {c['topic']} ({res.source}) {problems}")
        we = res.card.worked_example
        print("  HUMAN CHECK ->", we.problem, "|", " ; ".join(we.steps), "| =", we.answer)
    print(f"\n{len(cases) - failures}/{len(cases)} automatic checks passed")
    return 1 if failures else 0

sys.exit(asyncio.run(main()))
