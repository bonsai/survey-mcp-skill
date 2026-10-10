"""Minimal Semantic Scholar API client."""

import httpx

BASE_URL = "https://api.semanticscholar.org/graph/v1"


async def search_papers(query: str, limit: int = 10) -> list[dict]:
    """Search papers by query."""
    fields = "title,authors,year,abstract,citationCount,venue,url"
    params = {"query": query, "limit": limit, "fields": fields}
    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.get(f"{BASE_URL}/paper/search", params=params)
        resp.raise_for_status()
        data = resp.json()
        return data.get("data", [])
