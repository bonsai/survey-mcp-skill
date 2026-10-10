"""Pydantic models shared by FastAPI and MCP."""

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class Domain(str, Enum):
    paper = "paper"
    repo = "repo"
    marketing = "marketing"


class PaperInfo(BaseModel):
    title: str
    year: int | None = None
    authors: list[str] = Field(default_factory=list)
    abstract: str | None = None
    citation_count: int | None = None
    venue: str | None = None
    url: str | None = None


class RunSurveyRequest(BaseModel):
    query: str = Field(..., description="Survey question or keyword")
    domain: Domain = Field(Domain.paper, description="Survey domain")
    max_papers: int = Field(10, ge=1, le=50, description="Max papers to collect")


class RunSurveyResponse(BaseModel):
    run_id: str
    query: str
    domain: str
    summary: str
    paths: dict[str, str]


class SurveyListItem(BaseModel):
    run_id: str
    query: str
    domain: str
    created_at: str
    summary: str


class SurveyContentResponse(BaseModel):
    run_id: str
    format: str
    content: Any
