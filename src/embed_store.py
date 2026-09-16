"""
embed_store.py – Build the ProcurePrep ChromaDB vector store.

Run from the project root:
    python src/embed_store.py

Requires:
    GEMINI_API_KEY environment variable to be set.
"""

import os
import sys
import time

from dotenv import load_dotenv
import chromadb
from google import genai

# Load .env from the project root (no-op if already in environment).
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env"))

# Allow running from any working directory by resolving the project root.
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

from src.ingest import ingest_knowledge_corpus

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
COLLECTION_NAME = "procureprep_corpus"
CHROMA_DIR = os.path.join(PROJECT_ROOT, "chroma_db")
EMBED_MODEL = "models/gemini-embedding-001"
BATCH_SIZE = 10  # Gemini free tier: avoid hitting per-minute request limits

# ---------------------------------------------------------------------------
# Clients
# ---------------------------------------------------------------------------
api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    print("ERROR: GEMINI_API_KEY environment variable is not set.")
    sys.exit(1)

gemini = genai.Client(api_key=api_key)
chroma = chromadb.PersistentClient(path=CHROMA_DIR)

# Get-or-create the collection; running twice won't duplicate the collection.
collection = chroma.get_or_create_collection(name=COLLECTION_NAME)

# ---------------------------------------------------------------------------
# Ingest
# ---------------------------------------------------------------------------
knowledge_dir = os.path.join(PROJECT_ROOT, "knowledge")
chunks = ingest_knowledge_corpus(knowledge_dir=knowledge_dir)

if not chunks:
    print("No chunks found. Check that knowledge/ contains .txt files.")
    sys.exit(1)

# ---------------------------------------------------------------------------
# Embed and upsert in batches
# ---------------------------------------------------------------------------
unique_sources = {c["metadata"]["source_filename"] for c in chunks}

print(f"Embedding {len(chunks)} chunks from {len(unique_sources)} document(s)...")

for batch_start in range(0, len(chunks), BATCH_SIZE):
    batch = chunks[batch_start: batch_start + BATCH_SIZE]

    texts = [c["content"] for c in batch]
    ids = [
        f"{c['metadata']['source_filename']}_{c['metadata']['chunk_index']}"
        for c in batch
    ]
    metadatas = [
        {
            "source_filename": c["metadata"]["source_filename"],
            "chunk_index": c["metadata"]["chunk_index"],
            "provenance": c["metadata"]["provenance"],
        }
        for c in batch
    ]

    # Embed the batch
    response = gemini.models.embed_content(
        model=EMBED_MODEL,
        contents=texts,
        config={"task_type": "retrieval_document"},
    )
    embeddings = [e.values for e in response.embeddings]

    # Upsert — safe to run multiple times; existing IDs are overwritten.
    collection.upsert(
        ids=ids,
        embeddings=embeddings,
        documents=texts,
        metadatas=metadatas,
    )

    end = min(batch_start + BATCH_SIZE, len(chunks))
    print(f"  Upserted chunks {batch_start + 1}–{end} / {len(chunks)}")

    # Brief pause to respect API rate limits between batches.
    if end < len(chunks):
        time.sleep(1)

# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------
final_count = collection.count()
print()
print("=" * 50)
print("ProcurePrep – Embed Store Summary")
print("=" * 50)
print(f"  Documents (source files) : {len(unique_sources)}")
print(f"  Chunks embedded          : {len(chunks)}")
print(f"  Collection size (chroma) : {final_count}")
print(f"  Persist directory        : {CHROMA_DIR}")
print(f"  Collection name          : {COLLECTION_NAME}")
print("=" * 50)
