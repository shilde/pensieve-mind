import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from pensieve_mind.api.routes import embed, search

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("pensieve-mind starting up...")
    yield
    logger.info("pensieve-mind shutting down...")


app = FastAPI(
    title="pensieve-mind",
    description="Scraping and semantic embedding service for Pensieve",
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(embed.router, prefix="/api")
app.include_router(search.router, prefix="/api")

@app.get("/health")
def health() -> dict:
    return {"status": "ok"}
