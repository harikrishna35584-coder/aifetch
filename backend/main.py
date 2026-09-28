"""AIFetch - semantic search for AI tools.

Flow: user text -> embedding -> cosine similarity with tool embeddings -> top matches.
"""
import json
from pathlib import Path

import numpy as np
from fastapi import FastAPI, Query
from fastapi.staticfiles import StaticFiles
from sentence_transformers import SentenceTransformer

BASE_DIR = Path(__file__).parent
FRONTEND_DIR = BASE_DIR.parent / "frontend"
MIN_SCORE = 0.20  # ignore matches that are too weak

# 1. Load the embedding model (turns text into vectors that capture meaning)
model = SentenceTransformer("all-MiniLM-L6-v2")

# 2. Load our curated (verified) tools
tools = json.loads((BASE_DIR / "tools.json").read_text(encoding="utf-8"))

# 3. Convert every tool into one vector, once, at startup
tool_texts = [
    f"{t['name']}. {t['category']}. {t['description']} Tags: {', '.join(t['tags'])}"
    for t in tools
]
tool_vectors = model.encode(tool_texts, normalize_embeddings=True)

app = FastAPI(title="AIFetch")


@app.get("/api/search")
def search(q: str = Query(..., min_length=2), top_k: int = Query(6, ge=1, le=20)):
    # 4. Convert the user's text into a vector the same way
    query_vector = model.encode([q], normalize_embeddings=True)[0]

    # 5. Cosine similarity (vectors are normalised, so a dot product is enough)
    scores = tool_vectors @ query_vector

    # 6. Take the best matches, highest first
    best = np.argsort(scores)[::-1][:top_k]
    results = [
        {**tools[i], "verified": True, "score": round(float(scores[i]) * 100)}
        for i in best
        if scores[i] >= MIN_SCORE
    ]
    return {"query": q, "count": len(results), "results": results}


# Serve the web page at "/" (must come after the API routes)
app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")
