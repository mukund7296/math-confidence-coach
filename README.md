# Math Confidence Coach (prototype, part 1)

A private, no-chat tool. A teacher types a topic and gets one **Lesson Card**: the idea in plain words,
why it works, a worked example, common student mistakes (with how to respond), lesson ideas,
differentiation and a short activity. No accounts, no tests, no scores, no chat.

## Run it
```bash
python -m venv venv && source venv/bin/activate     # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env        # then fill in LLM_API_KEY (and check LLM_MODEL is currently available)
uvicorn app.main:app --reload                       # open http://localhost:8000
pytest -q                                           # 6 tests, no API key needed (LLM is faked)
python -m eval.run_eval                             # quality checks against the real model
```
Any OpenAI-compatible provider works (Gemini, Groq, OpenRouter, or local Ollama): change 3 env vars, no code.

## Product decisions
- **Need served:** "I must teach X tomorrow and I don't fully trust my own understanding." The card starts with the
  *teacher's* understanding (idea + why it works), then moves to teaching. Teachers who avoid chatbots and tests
  get one read-and-go page. No quiz, no score, nothing is judged.
- **Honesty about trust:** each card says whether it is based on a reviewed lesson (`/lessons`, 3 short originals
  I wrote) or is an AI-written draft the teacher should check. Math teachers who already doubt themselves must
  not be given confident wrong answers.
- **Languages:** 5 selectable, because the target is many countries.

## Architecture (small on purpose)
`static/index.html` -> `POST /coach` -> cache lookup -> (miss) retrieval of a vetted lesson -> LLM -> schema
validation (+1 retry) -> cache -> response.
- `app/llm.py` one provider-agnostic client. `app/retrieval.py` keyword lookup; swap for embeddings when the
  corpus grows past a few dozen lessons. `app/cache.py` SQLite now, Redis/Postgres for several servers.
- The API returns structured JSON, so any other client (mobile, LMS plugin) can reuse it.

## How I know answers are good
1. Output must pass a strict schema, otherwise retry once, otherwise a safe error (tested).
2. Grounding: if a reviewed lesson matches, the model must build on it.
3. `eval/run_eval.py`: structure, required concepts, banned test/score language, and it prints every worked example
   for a human to check. **Honest limit:** I have not had a maths teacher review outputs. Before launch: teacher
   review of the top ~200 topics, a "report a mistake" button, and cache invalidation of reported cards.
4. Unit tests cover caching, rate limit, input validation, bad model output.

## Cost per teacher per month
Per generated card: about 1.3k input + 1k output tokens. Cost = `calls x (in x price_in + out x price_out)`.
Example assumption (check the provider's current price list): $0.30 / 1M input, $2.50 / 1M output
=> about $0.003 per card. A teacher making 10 cards/month without cache: **about $0.03**.
Because the cache key is topic+grade+language and has no user data, 20-50k teachers hit mostly the same
topics; at an 80% hit rate it is **about $0.006 per teacher/month**, so 50,000 teachers cost roughly $300/month.
Further: pre-generate the ~500 most common topics in a batch (cheaper), use a smaller model for easy topics,
shorter output. Free tiers are only for development (rate-limited, see data section).

## Data: what we handle and where it goes
- The teacher types a **topic**, picks grade and language. Only that goes to the AI provider to write the card.
- We store the topic+grade+language and the generated card in a cache. **No names, emails, accounts or
  history.** IP addresses are kept only in server memory for one hour to limit abuse, never written to disk.
- Logs record failure reasons only, not topics.
- Free tiers of some providers may use prompts to improve their products. For production use a paid tier with
  no-training terms or an EU-hosted/local model; with GDPR in mind, sign a data processing agreement.
  Topics are not personal data, but teachers may type something personal, hence the notice under the form.

## Skipped and why
Accounts, history, chat, quizzes (the brief rejects them); vector DB (3 lessons); streaming; admin tool for
reviewing cards; real auth/CDN/monitoring. A "report a mistake" button is the first thing I would add.

## Time spent
FILL IN HONESTLY (e.g. ~2h). Commits show the order of work.
