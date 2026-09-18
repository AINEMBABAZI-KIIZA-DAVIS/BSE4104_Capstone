"""
retrieve.py – Query the ProcurePrep ChromaDB vector store.

Run from the project root:
    /opt/anaconda3/bin/python3 src/retrieve.py "What are the bid security requirements?"

Requires: GEMINI_API_KEY in environment or .env file.
"""

import os
import sys

from dotenv import load_dotenv

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(PROJECT_ROOT, ".env"))

import chromadb
from google import genai

COLLECTION_NAME = "procureprep_corpus"
CHROMA_DIR = os.path.join(PROJECT_ROOT, "chroma_db")
EMBED_MODEL = "models/gemini-embedding-001"

api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    print("ERROR: GEMINI_API_KEY environment variable is not set.")
    sys.exit(1)

gemini = genai.Client(api_key=api_key)
chroma = chromadb.PersistentClient(path=CHROMA_DIR)
collection = chroma.get_collection(name=COLLECTION_NAME)


def retrieve_relevant_chunks(query: str, top_k: int = 4) -> list[dict]:
    """Embed query and return top_k most similar chunks from the corpus."""
    response = gemini.models.embed_content(
        model=EMBED_MODEL,
        contents=[query],
        config={"task_type": "retrieval_query"},
    )
    query_embedding = response.embeddings[0].values

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
        include=["documents", "metadatas", "distances"],
    )

    chunks = []
    for text, meta, distance in zip(
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0],
    ):
        # ChromaDB returns L2 distance; convert to a 0-1 similarity score.
        similarity = 1 / (1 + distance)
        chunks.append({
            "text": text,
            "source_filename": meta["source_filename"],
            "chunk_index": meta["chunk_index"],
            "score": round(similarity, 4),
        })

    return chunks


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python src/retrieve.py \"<your query>\"")
        sys.exit(1)

    query = " ".join(sys.argv[1:])
    print(f"Query : {query}")
    print("=" * 60)

    hits = retrieve_relevant_chunks(query)

    for i, hit in enumerate(hits, 1):
        preview = hit["text"][:200].replace("\n", " ")
        print(f"[{i}] {hit['source_filename']}  (chunk {hit['chunk_index']})  score={hit['score']}")
        print(f"    {preview}...")
        print()
