"""
chatbot.py
==========
The brain of RaviBot.

ARCHITECTURE in plain English
-----------------------------
For every user question:

  1. Router  -> a tiny LLM call that returns "PERSONAL" or "GENERAL".
  2. If PERSONAL:
        a. embed the question
        b. pull the TOP_K most-similar chunks out of ChromaDB
        c. stuff them into the prompt as CONTEXT
        d. ask GPT-4o-mini to write the answer
        e. return answer + sources (so we can show citations)
  3. If GENERAL:
        a. send the question straight to GPT-4o-mini using the
           "general assistant" system prompt
        b. return answer (no sources, no retrieval)

The same `SupportBot`-style class can be imported from:
  - the Streamlit app  (chat_app.py)
  - the FastAPI server (api.py)
  - any other UI you build later.
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import List, Dict, Any

from dotenv import load_dotenv
from openai import OpenAI
import chromadb
from chromadb.config import Settings

import config
from prompts import (
    ROUTER_PROMPT,
    PERSONAL_PROMPT,
    GENERAL_PROMPT,
    USER_PROMPT_TEMPLATE,
)
from ingest import COLLECTION_NAME


# ----------------------------------------------------------------------
# Tiny data container for the bot's reply
# ----------------------------------------------------------------------
@dataclass
class Answer:
    text: str                                  # the response shown to the user
    mode: str                                  # "personal" or "general"
    sources: List[str] = field(default_factory=list)  # filenames (personal only)
    chunks:  List[str] = field(default_factory=list)  # raw retrieved text


# ----------------------------------------------------------------------
# Main bot class
# ----------------------------------------------------------------------
class RaviBot:
    """
    Create ONE instance at app startup, then call .ask() per question.
    """

    def __init__(self) -> None:
        # 1. read the .env file
        load_dotenv()
        if not os.getenv("OPENAI_API_KEY"):
            raise RuntimeError(
                "OPENAI_API_KEY is not set. Put it in a .env file."
            )

        # 2. open the OpenAI client (uses OPENAI_API_KEY automatically)
        self.openai = OpenAI()

        # 3. open the local ChromaDB collection (built by ingest.py)
        chroma = chromadb.PersistentClient(
            path=str(config.DB_DIR),
            settings=Settings(anonymized_telemetry=False),
        )
        try:
            self.collection = chroma.get_collection(COLLECTION_NAME)
        except Exception as e:
            raise RuntimeError(
                f"No vector DB collection '{COLLECTION_NAME}' found. "
                "Run `python ingest.py` first."
            ) from e

    # -----------------------------------------------------------------
    # PRIVATE — turn one string into a 1536-D embedding vector
    # -----------------------------------------------------------------
    def _embed(self, text: str) -> List[float]:
        resp = self.openai.embeddings.create(
            model=config.EMBEDDING_MODEL,
            input=[text],
        )
        return resp.data[0].embedding

    # -----------------------------------------------------------------
    # PRIVATE — search ChromaDB for the TOP_K closest chunks
    # -----------------------------------------------------------------
    def _retrieve(self, question: str, k: int = config.TOP_K) -> Dict[str, Any]:
        vec = self._embed(question)
        return self.collection.query(query_embeddings=[vec], n_results=k)

    # -----------------------------------------------------------------
    # PRIVATE — classify the question as PERSONAL or GENERAL
    # -----------------------------------------------------------------
    def _route(self, question: str) -> str:
        """Returns the string 'personal' or 'general'."""
        completion = self.openai.chat.completions.create(
            model=config.CHAT_MODEL,
            messages=[
                {"role": "system", "content": ROUTER_PROMPT},
                {"role": "user",   "content": question},
            ],
            temperature=0.0,           # we want a deterministic label
            max_tokens=4,              # one word
        )
        label = completion.choices[0].message.content.strip().upper()
        # default to PERSONAL on weird output (it's the safer/richer path)
        return "personal" if "PERSONAL" in label or "GENERAL" not in label else "general"

    # -----------------------------------------------------------------
    # PUBLIC — ask the bot a question
    # -----------------------------------------------------------------
    def ask(self,
            question: str,
            history: List[Dict[str, str]] | None = None) -> Answer:
        """
        Ask RaviBot a question.

        `history` is an optional list of past messages in OpenAI format:
            [{"role": "user", "content": "..."},
             {"role": "assistant", "content": "..."}]
        so the bot remembers earlier turns in the same chat.
        """
        history = history or []

        # ---- Step 1: classify ----
        mode = self._route(question)

        if mode == "personal":
            # ---- Step 2a: retrieve relevant chunks ----
            retrieved = self._retrieve(question)
            chunks  = retrieved["documents"][0]   if retrieved["documents"] else []
            metas   = retrieved["metadatas"][0]   if retrieved["metadatas"] else []
            sources = [m.get("source", "?") for m in metas]

            # ---- Step 2b: build the system message with context ----
            context_blocks = [
                f"[Source: {src}]\n{chunk}"
                for chunk, src in zip(chunks, sources)
            ]
            context = "\n\n".join(context_blocks) or "(no context found)"
            system_msg = {
                "role": "system",
                "content": PERSONAL_PROMPT.format(context=context),
            }

            # ---- Step 2c: assemble messages ----
            user_msg = {
                "role": "user",
                "content": USER_PROMPT_TEMPLATE.format(question=question),
            }
            messages = [system_msg, *history, user_msg]

            # ---- Step 2d: ask the LLM ----
            completion = self.openai.chat.completions.create(
                model=config.CHAT_MODEL,
                messages=messages,
                temperature=config.TEMPERATURE,
                max_tokens=config.MAX_RESPONSE_TOKENS,
            )
            text = completion.choices[0].message.content.strip()

            # de-duplicate source filenames, preserve order
            seen, unique_sources = set(), []
            for s in sources:
                if s not in seen:
                    seen.add(s)
                    unique_sources.append(s)

            return Answer(text=text, mode="personal",
                          sources=unique_sources, chunks=list(chunks))

        # ---------- GENERAL branch ----------
        system_msg = {"role": "system", "content": GENERAL_PROMPT}
        user_msg   = {"role": "user",   "content": question}
        messages   = [system_msg, *history, user_msg]

        completion = self.openai.chat.completions.create(
            model=config.CHAT_MODEL,
            messages=messages,
            temperature=config.TEMPERATURE,
            max_tokens=config.MAX_RESPONSE_TOKENS,
        )
        text = completion.choices[0].message.content.strip()
        return Answer(text=text, mode="general")


# ----------------------------------------------------------------------
# CLI playground — try it from the terminal: `python chatbot.py`
# ----------------------------------------------------------------------
if __name__ == "__main__":
    bot = RaviBot()
    print(f"{config.BOT_NAME} ready. Ask anything (type 'quit' to exit).\n")
    history: List[Dict[str, str]] = []
    while True:
        try:
            q = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if q.lower() in ("quit", "exit", "q"):
            break
        if not q:
            continue
        ans = bot.ask(q, history=history)
        print(f"\n{config.BOT_NAME} [{ans.mode}]: {ans.text}")
        if ans.sources:
            print(f"Sources: {', '.join(ans.sources)}")
        print()
        history.append({"role": "user", "content": q})
        history.append({"role": "assistant", "content": ans.text})
