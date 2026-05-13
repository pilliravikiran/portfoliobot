"""
api.py
======
A small REST API around RaviBot, so a website (e.g. your portfolio) can
talk to the bot from the browser.

Why FastAPI?
- Tiny boilerplate, automatic JSON in/out.
- Auto-generated docs at  http://localhost:8000/docs
- ASGI-based, runs blazingly fast under uvicorn.

Run it from the project folder:
    uvicorn api:app --reload --port 8000

Then visit:
    http://localhost:8000/docs        (interactive API explorer)
    http://localhost:8000/health      (liveness probe)
    POST http://localhost:8000/chat   (the chatbot)

CORS is wide-open here so your portfolio HTML can call this in dev.
TIGHTEN `allow_origins` before you deploy publicly.
"""
from __future__ import annotations

from typing import List, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

import config
from chatbot import RaviBot


# ----------------------------------------------------------------------
# 1. Spin up the bot once on startup (heavy: opens DB, loads embeddings)
# ----------------------------------------------------------------------
bot: Optional[RaviBot] = None

app = FastAPI(
    title=f"{config.BOT_NAME} API",
    description=(
        "Chat endpoint backed by OpenAI GPT-4o-mini + ChromaDB. "
        "Used by the Streamlit app AND the portfolio chat widget."
    ),
    version="1.0.0",
)

# CORS — allow any origin in dev. For production, replace with your domain.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://ravikiranpilli.com",
        "https://www.ravikiranpilli.com",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def _startup() -> None:
    global bot
    bot = RaviBot()


# ----------------------------------------------------------------------
# 2. Request / response shapes (Pydantic validates them automatically)
# ----------------------------------------------------------------------
class Message(BaseModel):
    role: str = Field(..., description="'user' or 'assistant'")
    content: str


class ChatRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=4000)
    history: List[Message] = Field(default_factory=list)


class ChatResponse(BaseModel):
    answer: str
    mode: str               # "personal" or "general"
    sources: List[str] = []


# ----------------------------------------------------------------------
# 3. Endpoints
# ----------------------------------------------------------------------
@app.get("/health")
def health() -> dict:
    """Cheap liveness probe — does NOT call OpenAI."""
    return {"status": "ok", "bot": config.BOT_NAME}


@app.get("/")
def root() -> dict:
    """A friendly landing JSON."""
    return {
        "name": f"{config.BOT_NAME} API",
        "docs": "/docs",
        "chat_endpoint": "POST /chat",
        "owner": config.OWNER_NAME,
    }


@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest) -> ChatResponse:
    """Ask the bot a question. Returns answer + classification + sources."""
    if bot is None:
        raise HTTPException(status_code=503, detail="Bot is still warming up.")

    try:
        history = [m.model_dump() for m in req.history]
        ans = bot.ask(req.question, history=history)
        return ChatResponse(
            answer=ans.text,
            mode=ans.mode,
            sources=ans.sources,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e
