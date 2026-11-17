"""One thin client for any OpenAI-compatible chat endpoint (Gemini, Groq, OpenRouter, Ollama...).
Switching provider = changing 3 env vars, no code change."""
import json
import os
import httpx


class LLMError(Exception):
    pass


def _extract_json(text: str) -> dict:
    text = text.strip()
    if text.startswith("```"):
        text = text.strip("`")
        text = text[text.find("{"):]
    start, end = text.find("{"), text.rfind("}")
    if start == -1 or end == -1:
        raise LLMError("model did not return JSON")
    return json.loads(text[start:end + 1])


async def complete_json(system: str, user: str) -> dict:
    base = os.getenv("LLM_BASE_URL", "").rstrip("/")
    key = os.getenv("LLM_API_KEY", "")
    model = os.getenv("LLM_MODEL", "")
    if not (base and key and model):
        raise LLMError("LLM is not configured (see .env.example)")
    body = {
        "model": model,
        "temperature": 0.3,
        "max_tokens": 1800,
        "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}],
    }
    if os.getenv("LLM_JSON_MODE", "true").lower() == "true":
        body["response_format"] = {"type": "json_object"}
    async with httpx.AsyncClient(timeout=60) as client:
        r = await client.post(f"{base}/chat/completions", json=body,
                              headers={"Authorization": f"Bearer {key}"})
    if r.status_code != 200:
        raise LLMError(f"provider returned {r.status_code}")   # never leak provider body to the browser
    try:
        return _extract_json(r.json()["choices"][0]["message"]["content"])
    except (KeyError, IndexError, json.JSONDecodeError) as e:
        raise LLMError("unreadable model output") from e
