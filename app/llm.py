
"""One provider-agnostic client for OpenAI-compatible LLM APIs."""

import json
import logging
import os

import httpx


logger = logging.getLogger(__name__)


class LLMError(Exception):
    pass


def _extract_json(text: str) -> dict:
    text = text.strip()

    if text.startswith("```"):
        text = text[text.find("{"):text.rfind("}") + 1]

    start = text.find("{")
    end = text.rfind("}")

    if start == -1 or end == -1:
        raise LLMError("Model did not return valid JSON.")

    try:
        result = json.loads(text[start:end + 1])
    except json.JSONDecodeError as exc:
        raise LLMError("Model returned malformed JSON.") from exc

    if not isinstance(result, dict):
        raise LLMError("Model response must be a JSON object.")

    return result


async def complete_json(system: str, user: str) -> dict:

    base = os.getenv("LLM_BASE_URL", "").rstrip("/")
    key = os.getenv("LLM_API_KEY", "")
    model = os.getenv("LLM_MODEL", "")

    if not all([base, key, model]):
        raise LLMError(
            "LLM is not configured. Check your .env file."
        )

    body = {
        "model": model,
        "temperature": 0.3,
        "max_tokens": 5000,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
    }

    if os.getenv("LLM_JSON_MODE", "true").lower() == "true":
        body["response_format"] = {"type": "json_object"}

    url = f"{base}/chat/completions"

    try:
        async with httpx.AsyncClient(timeout=60) as client:

            response = await client.post(
                url,
                json=body,
                headers={
                    "Authorization": f"Bearer {key}",
                    "Content-Type": "application/json",
                },
            )

    except httpx.RequestError as exc:
        logger.exception("LLM network request failed")
        raise LLMError("Could not connect to the AI provider.") from exc

    if response.status_code != 200:

        # Keep provider details in server logs, not in the browser.
        logger.error(
            "LLM provider error: status=%s, response=%s",
            response.status_code,
            response.text[:2000],
        )

        raise LLMError(
            f"AI provider returned HTTP {response.status_code}."
        )

    try:
        content = response.json()["choices"][0]["message"]["content"]

        if not isinstance(content, str):
            raise LLMError("Unexpected model response format.")

        return _extract_json(content)

    except (KeyError, IndexError, json.JSONDecodeError) as exc:
        logger.exception("Could not parse LLM response")
        raise LLMError("Model returned an unreadable response.") from exc
