from pydantic import BaseModel, HttpUrl, field_validator
from uuid import UUID

class EmbedRequest(BaseModel):
    bookmark_id: UUID
    url: str

    @field_validator("url")
    @classmethod
    def url_must_be_valid(cls, v: str) -> str:
        if not v.startswith(("http://", "https://")):
            raise ValueError("URL must start with http:// or https://")
        return v

class EmbedResponse(BaseModel):
    bookmark_id: UUID
    emedding_id: str
    title: str | None
    desription: str | None
    content_snippet: str | None

class SearchResult(BaseModel):
    bookmark_id: UUID
    score: float

class SearchResponse(BaseModel):
    results: list[SearchResult]
    query: str