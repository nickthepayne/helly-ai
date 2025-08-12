from fastapi import FastAPI
from helly_ai.api.routers import router
import logging
import os

# Ensure INFO-level logging in dev so startup/endpoint logs are visible
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")

app = FastAPI(title="Helly AI", version="0.1.0")
app.include_router(router)

logger = logging.getLogger("helly_ai")

@app.on_event("startup")
async def on_startup():
    # Minimal startup log for dev visibility
    model = os.getenv("OPENROUTER_MODEL", "dev-mock")
    chroma_dir = os.getenv("CHROMA_PERSIST_DIR", ".chroma")
    logger.info("Helly AI started (model=%s, chroma_dir=%s)", model, chroma_dir)

