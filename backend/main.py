from __future__ import annotations

import logging
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

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
app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=os.environ.get(
        "BACKEND_CORS_ORIGIN_REGEX",
        r"https?://(localhost|127\.0\.0\.1):30[0-9]{2}",
    ),
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type"],
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
