from __future__ import annotations

import logging

from fastapi import FastAPI

from backend.app.routers import api_router

if not logging.getLogger().handlers:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )

app = FastAPI(
    title="K-Labor Shield Retrieval API",
    version="0.1.0",
)
app.include_router(api_router)


@app.get("/", tags=["health"])
def root() -> dict[str, str]:
    return {
        "service": "retrieval",
        "status": "ok",
    }


@app.get("/health", tags=["health"])
def health() -> dict[str, str]:
    return {"status": "ok"}
