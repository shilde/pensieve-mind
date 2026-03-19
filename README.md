# pensieve-mind

Scraping and semantic embedding microservice for [Pensieve](https://github.com/). Receives bookmark URLs from `pensieve-api`, scrapes their content, generates local embeddings, and stores them in Qdrant for semantic search.

## How it fits in

```
pensieve-api  →  POST /api/embed        →  scrape URL → embed → upsert into Qdrant
pensieve-api  →  DELETE /api/embed/:id  →  remove embedding from Qdrant
client        →  GET /api/search?q=...  →  embed query → nearest-neighbour search → ranked bookmark IDs
```

## Requirements

- Python 3.11+
- [Qdrant](https://qdrant.tech/) running on `localhost:6333` (or configured via env)

## Setup

```bash
# Install dependencies
pip install -e ".[dev]"

# Install Playwright browsers (needed for scraping)
playwright install chromium

# Copy and edit config
cp src/pensieve_mind/.env.example .env
```

## Running

```bash
uvicorn pensieve_mind.main:app --reload
```

The service starts on `http://localhost:8000`. Check `GET /health` to verify it's up.

## Configuration

All settings are read from a `.env` file (or environment variables):

| Variable | Default | Description |
|---|---|---|
| `QDRANT_HOST` | `localhost` | Qdrant host |
| `QDRANT_PORT` | `6333` | Qdrant port |
| `QDRANT_COLLECTION` | `pensieve` | Collection name |
| `EMBEDDING_MODEL` | `all-MiniLM-L6-v2` | sentence-transformers model (runs locally) |
| `EMBEDDING_DIMENSION` | `384` | Vector dimension (must match model) |
| `SCRAPER_TIMEOUT_SECONDS` | `30` | Per-request scrape timeout |
| `SCRAPER_MAX_CONTENT_LENGTH` | `50000` | Max characters of page content to embed |

## API

### `POST /api/embed`

Scrape a URL and store its embedding.

```json
// Request
{ "bookmark_id": "<uuid>", "url": "https://example.com" }

// Response 201
{
  "bookmark_id": "<uuid>",
  "embedding_id": "<uuid>",
  "title": "Page title",
  "description": "Meta description",
  "content_snippet": "First 300 chars of content..."
}
```

### `DELETE /api/embed/{bookmark_id}`

Remove the embedding for a bookmark. Returns `204 No Content`.

### `GET /api/search?q=<query>`

Semantic search over stored embeddings.

| Param | Required | Default | Description |
|---|---|---|---|
| `q` | yes | — | Natural-language query |
| `limit` | no | `10` | Max results (1–100) |
| `collection_id` | no | — | Filter by collection UUID |

```json
// Response 200
{
  "query": "kubernetes deployment strategies",
  "results": [
    { "bookmark_id": "<uuid>", "score": 0.92 },
    ...
  ]
}
```

## Development

```bash
# Run all tests
pytest

# Run a single test file
pytest tests/test_embed_route.py

# Run a single test
pytest tests/test_embed_route.py::test_embed_returns_201
```

Tests mock `MindService` via FastAPI dependency overrides — no Qdrant instance required.

## Architecture

```
src/pensieve_mind/
├── main.py                  # FastAPI app + lifespan
├── config.py                # Settings (pydantic-settings)
├── dependencies.py          # Lazy MindService singleton for DI
├── api/
│   ├── routes/
│   │   ├── embed.py         # POST /embed, DELETE /embed/:id
│   │   └── search.py        # GET /search
│   └── dto/
│       └── schemas.py       # Pydantic request/response models
├── scraping/
│   └── scraper.py           # Playwright + BeautifulSoup4 scraper
├── embedding/
│   └── embedding_service.py # sentence-transformers + Qdrant client
└── search/
    └── mind_service.py      # Orchestrates scrape → embed → store/search
```
