import json
import re
from pathlib import Path
from collections import Counter

from fastapi import FastAPI, Query
from fastapi.staticfiles import StaticFiles

BASE_DIR = Path(__file__).parent
FRONTEND_DIR = BASE_DIR.parent / "frontend"

# Load AI tools
tools = json.loads(
    (BASE_DIR / "tools.json").read_text(encoding="utf-8")
)

app = FastAPI(title="AIFetch")


def tokenize(text):
    """Convert text into simple searchable words."""
    return set(re.findall(r"[a-z0-9]+", text.lower()))


# Prepare searchable text for every tool
tool_data = []

for tool in tools:
    text = (
        f"{tool['name']} "
        f"{tool['category']} "
        f"{tool['description']} "
        f"{' '.join(tool['tags'])}"
    )

    tool_data.append({
        "tool": tool,
        "words": tokenize(text)
    })


@app.get("/api/search")
def search(
    q: str = Query(..., min_length=2),
    top_k: int = Query(6, ge=1, le=20)
):
    query_words = tokenize(q)
    results = []

    for item in tool_data:
        common_words = query_words & item["words"]

        if common_words:
            score = len(common_words) / max(len(query_words), 1)
            results.append((score, item["tool"]))

    # Highest matching score first
    results.sort(key=lambda x: x[0], reverse=True)

    final_results = []

    for score, tool in results[:top_k]:
        final_results.append({
            **tool,
            "verified": True,
            "score": round(score * 100)
        })

    return {
        "query": q,
        "count": len(final_results),
        "results": final_results
    }


# Serve frontend
app.mount(
    "/",
    StaticFiles(directory=FRONTEND_DIR, html=True),
    name="frontend"
)