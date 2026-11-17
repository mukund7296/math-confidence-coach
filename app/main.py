import logging
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

load_dotenv()

from . import cache
from .coach import make_card, PROMPT_VERSION
from .llm import LLMError
from .schema import CoachRequest, CoachResponse

log = logging.getLogger("coach")

app = FastAPI(title="Math Confidence Coach")

STATIC = Path(__file__).resolve().parent.parent / "static"
app.mount("/static", StaticFiles(directory=STATIC), name="static")


@app.get("/")
def home():
    return FileResponse(STATIC / "index.html")


@app.get("/health")
def health():
    return {"ok": True}


@app.post("/coach", response_model=CoachResponse)
async def coach(req: CoachRequest, request: Request):
    # 1. Check cache first
    key = cache.make_key(req.topic, req.grade, req.language, PROMPT_VERSION)
    hit = cache.get(key)
    if hit:
        res = CoachResponse.model_validate_json(hit)
        res.cached = True
        return res

    # 2. Simple rate limiting by IP
    ip = request.client.host if request.client else "unknown"
    if not cache.allow(ip):
        raise HTTPException(status_code=429, detail="Please try again a little later.")

    # 3. Generate the card
    try:
        res = await make_card(req)
    except LLMError as e:
        log.error("generation failed: %s", e)
        # Temporary: show real error for debugging
        raise HTTPException(
            status_code=502,
            detail=f"Debug: {str(e)}"
        )

    # 4. Save to cache and return
    cache.put(key, res.model_dump_json())
    return res