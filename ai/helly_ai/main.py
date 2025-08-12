import logging
import os
from dotenv import load_dotenv
from fastapi import FastAPI

# Ensure INFO-level logging in dev so startup/endpoint logs are visible
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
logger = logging.getLogger("helly_ai")


def load_dotenv_if_present():
    """Load KEY=VALUE pairs from ai/.env if present using python-dotenv.
    Existing process env vars take precedence (override=False).
    """
    here = os.path.dirname(__file__)
    root = os.path.abspath(os.path.join(here, ".."))  # ai/
    env_path = os.path.join(root, ".env")
    if os.path.exists(env_path):
        loaded = load_dotenv(env_path, override=False)
        if loaded:
            logger.info("Loaded environment from .env (ai/.env)")
    else:
        # Not an error; just informational for devs
        logger.debug("No ai/.env file found; relying on process environment")


# Load .env before importing routers that construct services using env
load_dotenv_if_present()

from helly_ai.api.routers import router  # noqa: E402 (import after env load)

app = FastAPI(title="Helly AI", version="0.1.0")
app.include_router(router)


@app.on_event("startup")
async def on_startup():
    # Minimal startup log for dev visibility
    model = os.getenv("OPENROUTER_MODEL", "dev-mock")
    chroma_dir = os.getenv("CHROMA_PERSIST_DIR", ".chroma")
    logger.info("Helly AI started (model=%s, chroma_dir=%s)", model, chroma_dir)

