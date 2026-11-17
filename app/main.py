import logging
from pathlib import Path
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

load_dotenv()
from . import cache                      # noqa: E402
from .coach import make_card, PROMPT_VERSION   # noqa: E402
from .llm import LLMError                # noqa: E402
from .schema import CoachRequest, CoachResponse   # noqa: E402

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
    key = cache.make_key(req.topic, req.grade, req.language, PROMPT_VERSION)
    hit = cache.get(key)
    if hit:
        res = CoachResponse.model_validate_json(hit)
        res.cached = True
        return res
    ip = request.client.host if request.client else "unknown"
    if not cache.allow(ip):
        raise HTTPException(429, "Please try again a little later.")
    try:
        res = await make_card(req)
    except LLMError as e:
        log.warning("generation failed: %s", e)   # log reason only, never the topic or IP
        raise HTTPException(502, "The coach could not prepare this card right now. Please try again.")
    cache.put(key, res.model_dump_json())
    return res
