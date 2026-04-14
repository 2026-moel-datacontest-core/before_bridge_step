from __future__ import annotations

from fastapi import APIRouter

from .answer import router as answer_router
from .retrieval import router as retrieval_router

api_router = APIRouter()
api_router.include_router(retrieval_router)
api_router.include_router(answer_router)

__all__ = ["api_router"]
