"""
ingest.py
=========
Build the knowledge base.

WHAT THIS SCRIPT DOES (in plain English):
  1. Walk the `data/` folder and read every .txt / .md / .pdf / .docx file.
  2. Cut each document into small overlapping pieces called CHUNKS.
  3. Ask OpenAI's embedding model to turn each chunk into 1536 numbers.
     Two pieces of text that mean the same thing get similar numbers,
     so we can search by MEANING (not just keywords).
  4. Save all (chunk text + numbers + source filename) into a local
     vector database called ChromaDB. The database lives on disk in
     `chroma_db/`, so the indexing is a one-time cost.

WHEN DO I RUN THIS?
  Run it once after you set up.
  Run it again any time you add / edit / delete a file in data/.

USAGE:
    python ingest.py
"""
from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import List, Tuple

from dotenv import load_dotenv
from openai import OpenAI
import chromadb
from chromadb.config import Settings
from tqdm import tqdm
from pypdf import PdfReader

import config


# ----------------------------------------------------------------------
# 1. READ a file from disk and return its plain text
# ----------------------------------------------------------------------
def read_file(path: Path) -> str:
    """Return the text content of a .txt / .md / .pdf / .docx file."""
    suffix = path.suffix.lower()

    if suffix in (".txt", ".md"):
        return path.read_text(encoding="utf-8")

    if suffix == ".pdf":
        reader = PdfReader(str(path))
        pages = [page.extract_text() or "" for page in reader.pages]
        return "\n".join(pages)

    if suffix == ".docx":
        # Lazy import so people who only have .md files don't need python-docx.
        from docx import Document
        doc = Document(str(path))
        return "\n".join(p.text for p in doc.paragraphs)

    raise ValueError(f"Unsupported file type: {path.name}")


# ----------------------------------------------------------------------
# 2. SPLIT a long string into overlapping chunks
# ----------------------------------------------------------------------
def chunk_text(text: str,
               size: int = config.CHUNK_SIZE,
               overlap: int = config.CHUNK_OVERLAP) -> List[str]:
    """
    Slide a window of `size` characters across `text`, moving forward by
    (size - overlap) each step. Overlap means a sentence on the boundary
    still appears whole in at least one chunk.
    """
    text = text.strip()
    if not text:
        return []

    chunks: List[str] = []
    step = max(1, size - overlap)
    for start in range(0, len(text), step):
        end = start + size
        piece = text[start:end].strip()
        if piece:
            chunks.append(piece)
        if end >= len(text):
            break
    return chunks


# ----------------------------------------------------------------------
# 3. ASK OpenAI to embed a batch of strings
# ----------------------------------------------------------------------
def embed_texts(client: OpenAI, texts: List[str]) -> List[List[float]]:
    """Return one vector (list of floats) per input string."""
    response = client.embeddings.create(
        model=config.EMBEDDING_MODEL,
        input=texts,
    )
    return [item.embedding for item in response.data]


# ----------------------------------------------------------------------
# 4. OPEN (or wipe + recreate) the Chroma collection on disk
# ----------------------------------------------------------------------
COLLECTION_NAME = "ravibot_docs"


def get_collection(reset: bool = False):
    """Open the local Chroma database stored on disk."""
    client = chromadb.PersistentClient(
        path=str(config.DB_DIR),
        settings=Settings(anonymized_telemetry=False),
    )
    if reset:
        try:
            client.delete_collection(COLLECTION_NAME)
        except Exception:
            pass  # collection didn't exist yet — fine
    return client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},  # cosine distance for embeddings
    )


# ----------------------------------------------------------------------
# 5. MAIN — run the full pipeline
# ----------------------------------------------------------------------
def main(reset: bool = True) -> None:
    load_dotenv()
    if not os.getenv("OPENAI_API_KEY"):
        print("ERROR: OPENAI_API_KEY not set.")
        print("  Did you copy .env.example to .env and paste your real key?")
        sys.exit(1)

    client = OpenAI()
    collection = get_collection(reset=reset)

    data_dir = config.DATA_DIR
    if not data_dir.exists():
        print(f"ERROR: data folder not found at {data_dir}")
        sys.exit(1)

    files = sorted(
        p for p in data_dir.rglob("*")
        if p.suffix.lower() in (".txt", ".md", ".pdf", ".docx")
    )
    if not files:
        print("No .txt / .md / .pdf / .docx files in data/. Add some and retry.")
        sys.exit(0)

    print(f"Found {len(files)} document(s) to index.")

    # 5a. read + chunk every file
    all_chunks: List[Tuple[str, str]] = []   # (chunk_text, source_filename)
    for path in files:
        print(f"  reading {path.name} ...")
        try:
            raw = read_file(path)
        except Exception as e:
            print(f"    skipped: {e}")
            continue
        for c in chunk_text(raw):
            all_chunks.append((c, path.name))

    if not all_chunks:
        print("No chunks produced — files might be empty.")
        sys.exit(0)

    print(f"Produced {len(all_chunks)} chunks. Embedding with OpenAI ...")

    # 5b. embed in batches of 64 to stay well under request limits
    BATCH = 64
    ids, docs, metas, vecs = [], [], [], []
    next_id = 0
    for i in tqdm(range(0, len(all_chunks), BATCH)):
        batch = all_chunks[i : i + BATCH]
        texts = [t for t, _ in batch]
        embeddings = embed_texts(client, texts)
        for (text, source), vec in zip(batch, embeddings):
            ids.append(f"chunk-{next_id}")
            docs.append(text)
            metas.append({"source": source})
            vecs.append(vec)
            next_id += 1

    # 5c. add everything to Chroma in one call
    collection.add(ids=ids, documents=docs, metadatas=metas, embeddings=vecs)

    print("")
    print(f"Done. Indexed {len(ids)} chunks from {len(files)} document(s).")
    print(f"Vector DB stored at: {config.DB_DIR}")


# ----------------------------------------------------------------------
if __name__ == "__main__":
    # `reset=True` wipes the old collection so the DB always matches data/.
    main(reset=True)
