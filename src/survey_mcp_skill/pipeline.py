"""Survey execution pipeline."""

import httpx

from .arxiv_client import search_arxiv
from .models import PaperInfo
from .outputs import save_survey
from .semantic_scholar import search_papers


async def run_survey(query: str, domain: str, max_papers: int = 10) -> dict:
    """Run a survey for the given query and domain."""
    if domain != "paper":
        raise NotImplementedError(f"domain '{domain}' is not implemented yet")

    try:
        raw_papers = await search_papers(query, max_papers)
    except httpx.HTTPStatusError as exc:
        if exc.response.status_code == 429:
            raw_papers = search_arxiv(query, max_papers)
        else:
            raise

    papers: list[PaperInfo] = []
    for item in raw_papers:
        authors = [a.get("name", "") for a in item.get("authors", []) if a.get("name")]
        papers.append(
            PaperInfo(
                title=item.get("title") or "Unknown",
                year=item.get("year"),
                authors=authors,
                abstract=item.get("abstract"),
                citation_count=item.get("citationCount"),
                venue=item.get("venue"),
                url=item.get("url"),
            )
        )

    top = max(papers, key=lambda p: p.citation_count or 0) if papers else None
    if top and top.citation_count is not None:
        top_str = f"Top cited: {top.title} ({top.citation_count} citations)."
    elif top:
        top_str = f"Top result: {top.title}."
    else:
        top_str = ""
    summary = f"Found {len(papers)} papers for '{query}'. {top_str}".strip()

    paths = save_survey(query, domain, papers, summary)

    return {
        "run_id": paths["md"].split("/")[-1].replace(".md", ""),
        "query": query,
        "domain": domain,
        "summary": summary,
        "paths": paths,
    }
