"""FastAPI app + FastMCP server."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastmcp import FastMCP

from .models import (
    Domain,
    RunSurveyRequest,
    RunSurveyResponse,
    SurveyContentResponse,
    SurveyListItem,
)
from .outputs import get_survey_content, init_db, list_surveys
from .pipeline import run_survey


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(
    title="survey-mcp-skill",
    description="Conversational local survey agent with MCP / OpenAPI / FastAPI",
    version="0.1.0",
    lifespan=lifespan,
)


@app.post("/surveys", operation_id="run_survey", response_model=RunSurveyResponse)
async def api_run_survey(req: RunSurveyRequest):
    """Run a survey and persist all output formats."""
    return await run_survey(req.query, req.domain.value, req.max_papers)


@app.get("/surveys", operation_id="list_surveys", response_model=list[SurveyListItem])
async def api_list_surveys(limit: int = 10):
    """List recent surveys."""
    return list_surveys(limit)


@app.get("/surveys/{run_id}", operation_id="get_survey", response_model=SurveyContentResponse)
async def api_get_survey(run_id: str, fmt: str = "md"):
    """Get a saved survey in md, json, or html."""
    content = get_survey_content(run_id, fmt)
    return {"run_id": run_id, "format": fmt, "content": content}


mcp = FastMCP.from_fastapi(app, name="survey-mcp-skill")
