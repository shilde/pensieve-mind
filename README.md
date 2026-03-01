# pensieve-mind

Python / FastAPI service for Pensieve. Handles scraping and semantic embeddings.

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn src.pensieve_mind.main:app --reload --port 8081
```
