# AIFetch – Verified AI Tools Discovery Platform

Type what you need in plain English (e.g. *"I need a tool to create images from text"*) and AIFetch finds the most relevant AI tools using **semantic search**, not just keyword matching.

## How to run

```bash
pip install -r requirements.txt
cd backend
uvicorn main:app --reload
```

Open **http://localhost:8000**. (API docs are at `/docs`.)
The first run downloads a small model (~90 MB), so it needs internet once.

## Project structure

```
aifetch/
├── backend/
│   ├── main.py       # FastAPI app: loads model, embeds tools, /api/search
│   └── tools.json    # Curated list of verified AI tools (name, category, description, tags, url)
├── frontend/
│   └── index.html    # Search page (plain HTML + CSS + JS)
├── requirements.txt
└── README.md
```

## How it works (explain it in 4 steps)

1. **Curated data** – `tools.json` holds verified AI tools with a description and tags.
2. **Embeddings** – At startup, each tool's text is converted into a vector (a list of numbers that represents its *meaning*) using the `all-MiniLM-L6-v2` sentence-transformer model.
3. **Query** – The user's sentence is converted into a vector with the same model.
4. **Similarity** – We compare the query vector with every tool vector using **cosine similarity** and return the top matches, highest score first.

That is why *"make pictures from a sentence"* still finds Midjourney or Ideogram, even though those exact words never appear in their descriptions.

## API

`GET /api/search?q=<text>&top_k=6`

```json
{
  "query": "I need a text to image creation tool",
  "count": 6,
  "results": [
    { "name": "Ideogram", "category": "Image Generation", "description": "...",
      "pricing": "Freemium", "url": "https://ideogram.ai", "verified": true, "score": 58 }
  ]
}
```

## Interview questions you should be ready for

**What is semantic search and how is it different from keyword search?**
Keyword search matches exact words. Semantic search matches meaning, using embeddings, so different wording with the same intent still matches.

**What is an embedding?**
A fixed-length vector of numbers produced by a model so that texts with similar meaning end up close together.

**Why cosine similarity?**
It measures the angle between two vectors, so it compares meaning direction and ignores text length. With normalised vectors it is just a dot product, which is fast.

**Why compute tool embeddings at startup?**
Tool data rarely changes, so we embed once and reuse. Only the user's query is embedded per request.

**What does the score threshold do?**
`MIN_SCORE` drops weak matches so unrelated tools are not shown for vague or off-topic queries.

**Why FastAPI?**
Simple, fast, automatic validation (the `min_length` on `q`), and free interactive docs at `/docs`.

**How do you keep the tools "verified"?**
Tools are added manually to `tools.json` after checking the official site. Nothing is scraped automatically.

**How would you scale this?**
Move tools to a database, store vectors in a vector database (FAISS, Chroma or pgvector), add new tools through an admin flow, and cache frequent queries.

## Possible improvements (mention, don't build)

- Category and pricing filters
- Live web search for tools not in the database
- User ratings and reviews
- Vector database instead of an in-memory array
