from fastapi import FastAPI
from helly_ai.api.routers import router

app = FastAPI(title="Helly AI", version="0.1.0")
app.include_router(router)

