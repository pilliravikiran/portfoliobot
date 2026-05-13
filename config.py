"""
config.py
=========
All the knobs of the chatbot live here, in ONE place.
If you ever want to change a model name, a chunk size, or a file path,
do it here — not deep inside the code.

Beginner notes:
- "Model" means "which AI to ask".
- "Embedding" means "turn text into numbers so we can search by meaning".
- "Chunk" means "a small piece of a bigger document".
"""
from pathlib import Path
import os
from dotenv import load_dotenv

# Load the .env file FIRST so any environment overrides below take effect.
load_dotenv()

# ----------------------------------------------------------------------
# 1. Which OpenAI models to use
# ----------------------------------------------------------------------
# gpt-4o-mini  -> the writer. Cheap, fast, smart enough for almost anything.
# text-embedding-3-small -> the meaning-finder. Turns text into 1536 numbers.
CHAT_MODEL      = os.getenv("CHAT_MODEL",      "gpt-4o-mini")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")

# ----------------------------------------------------------------------
# 2. Chunking — how we slice documents before storing them
# ----------------------------------------------------------------------
# Think of a chunk like a Post-it note. Too small (50 chars) = no context.
# Too big (5000 chars) = the AI gets distracted by unrelated text.
# 800 with 150 overlap is the sweet spot.
CHUNK_SIZE    = 800
CHUNK_OVERLAP = 150

# ----------------------------------------------------------------------
# 3. Retrieval — how many chunks to pull per question
# ----------------------------------------------------------------------
# We grab the TOP_K most-similar chunks for every question.
TOP_K = 5

# ----------------------------------------------------------------------
# 4. Generation — controls the LLM's behaviour
# ----------------------------------------------------------------------
# Low temperature  = more factual, predictable.
# High temperature = more creative, more "hallucination" risk.
# For a personal assistant we want factual, so we keep it low-ish.
TEMPERATURE         = 0.3
MAX_RESPONSE_TOKENS = 700

# ----------------------------------------------------------------------
# 5. File paths — where everything lives on disk
# ----------------------------------------------------------------------
ROOT_DIR = Path(__file__).parent
DATA_DIR = ROOT_DIR / "data"          # Source documents about Ravi
DB_DIR   = ROOT_DIR / "chroma_db"     # Vector database (auto-created)

# The bot's name (shown in the UIs)
BOT_NAME = "PortfolioBot"

# Who built this bot — used in the system prompt
OWNER_NAME  = "Ravi Kiran Pilli"
OWNER_TITLE = "AI-Powered Full Stack Engineer"
OWNER_EMAIL = "mail2pilliravikiran@gmail.com"
