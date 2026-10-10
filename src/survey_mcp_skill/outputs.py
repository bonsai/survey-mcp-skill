"""Persist survey results to DB / Markdown / JSON / HTML / llm-wiki."""

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from .models import PaperInfo


def _home() -> Path:
    return Path.home()


def _data_dir() -> Path:
    d = _home() / "data-survey-mcp-skill"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _db_path() -> Path:
    d = _home() / ".db"
    d.mkdir(parents=True, exist_ok=True)
    return d / "survey_mcp_skill.db"


def _wiki_dir() -> Path:
    d = _home() / "llm-wiki" / "survey-mcp-skill"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _slugify(text: str) -> str:
    return "_".join(
        "".join(c if c.isalnum() else " " for c in text.lower()).split()[:6]
    )


def _run_id(query: str, domain: str) -> str:
    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    return f"done_{ts}_{domain}_{_slugify(query)}"[:80]


def init_db() -> None:
    """Create SQLite tables if they do not exist."""
    with sqlite3.connect(_db_path()) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS surveys (
                run_id TEXT PRIMARY KEY,
                query TEXT NOT NULL,
                domain TEXT NOT NULL,
                created_at TEXT NOT NULL,
                summary TEXT NOT NULL,
                md_path TEXT NOT NULL,
                json_path TEXT NOT NULL,
                html_path TEXT NOT NULL,
                wiki_path TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS papers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                run_id TEXT NOT NULL,
                title TEXT NOT NULL,
                year INTEGER,
                authors TEXT,
                abstract TEXT,
                citation_count INTEGER,
                venue TEXT,
                url TEXT,
                FOREIGN KEY (run_id) REFERENCES surveys(run_id)
            )
            """
        )


def _build_markdown(
    run_id: str,
    query: str,
    domain: str,
    created_at: str,
    summary: str,
    papers: list[PaperInfo],
) -> str:
    lines = [
        f"# Survey: {query}",
        "",
        f"- **Domain:** {domain}",
        f"- **Run ID:** {run_id}",
        f"- **Created:** {created_at}",
        "",
        "## Summary",
        "",
        summary,
        "",
        f"## Papers ({len(papers)})",
        "",
        "| # | Year | Title | Authors | Citations | Venue |",
        "|---|------|-------|---------|-----------|-------|",
    ]
    for i, p in enumerate(papers, 1):
        authors = ", ".join(p.authors[:3]) or "-"
        title = p.title.replace("|", "\\|")
        venue = (p.venue or "-").replace("|", "\\|")
        year = p.year or "-"
        citations = p.citation_count or "-"
        lines.append(f"| {i} | {year} | {title} | {authors} | {citations} | {venue} |")
    lines.append("")
    return "\n".join(lines)


def _build_html(
    run_id: str,
    query: str,
    domain: str,
    created_at: str,
    summary: str,
    papers: list[PaperInfo],
) -> str:
    rows = []
    for i, p in enumerate(papers, 1):
        authors = ", ".join(p.authors[:3]) or "-"
        title = p.title
        url = p.url or ""
        title_cell = f'<a href="{url}">{title}</a>' if url else title
        rows.append(
            f"<tr><td>{i}</td><td>{p.year or '-'}</td>"
            f"<td>{title_cell}</td><td>{authors}</td>"
            f"<td>{p.citation_count or '-'}</td><td>{p.venue or '-'}</td></tr>"
        )
    rows_html = "\n".join(rows)
    return f"""<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<title>Survey: {query}</title>
<style>
body {{ font-family: sans-serif; max-width: 960px; margin: 2rem auto; padding: 0 1rem; }}
table {{ border-collapse: collapse; width: 100%; margin-top: 1rem; }}
th, td {{ border: 1px solid #ccc; padding: 0.5rem; text-align: left; }}
th {{ background: #f5f5f5; }}
</style>
</head>
<body>
<h1>Survey: {query}</h1>
<p><strong>Domain:</strong> {domain} | <strong>Run ID:</strong> {run_id} | <strong>Created:</strong> {created_at}</p>
<h2>Summary</h2>
<p>{summary}</p>
<h2>Papers ({len(papers)})</h2>
<table>
<thead><tr><th>#</th><th>Year</th><th>Title</th><th>Authors</th><th>Citations</th><th>Venue</th></tr></thead>
<tbody>
{rows_html}
</tbody>
</table>
</body>
</html>
"""


def _build_wiki_markdown(
    run_id: str,
    query: str,
    domain: str,
    created_at: str,
    summary: str,
    papers: list[PaperInfo],
) -> str:
    lines = [
        f"# Recap: {query}",
        "",
        f"- **Domain:** {domain}",
        f"- **Run ID:** {run_id}",
        f"- **Created:** {created_at}",
        "",
        "## One-line summary",
        "",
        summary,
        "",
        "## Notable items",
        "",
    ]
    for p in papers[:5]:
        authors = ", ".join(p.authors[:3]) or "-"
        lines.append(f"- **{p.title}** ({p.year or '?'}) — {authors}. {p.venue or ''}")
    lines.append("")
    return "\n".join(lines)


def save_survey(
    query: str,
    domain: str,
    papers: list[PaperInfo],
    summary: str,
    run_id: str | None = None,
) -> dict[str, str]:
    """Persist a survey to all output formats and the ledger DB."""
    init_db()
    if run_id is None:
        run_id = _run_id(query, domain)
    created_at = _now_iso()
    date_dir = _data_dir() / datetime.now(timezone.utc).strftime("%Y-%m-%d")
    date_dir.mkdir(parents=True, exist_ok=True)

    md_path = date_dir / f"{run_id}.md"
    json_path = date_dir / f"{run_id}.json"
    html_path = date_dir / f"{run_id}.html"
    wiki_path = _wiki_dir() / f"{run_id}.md"

    # Step 1: Primary artifact — Markdown report
    md = _build_markdown(run_id, query, domain, created_at, summary, papers)
    md_path.write_text(md, encoding="utf-8")

    # Step 2: Derived structured artifacts — JSON / HTML
    html = _build_html(run_id, query, domain, created_at, summary, papers)
    payload = {
        "run_id": run_id,
        "query": query,
        "domain": domain,
        "created_at": created_at,
        "summary": summary,
        "papers": [p.model_dump() for p in papers],
    }
    html_path.write_text(html, encoding="utf-8")
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    # Step 3: Derived recap — llm-wiki (summarized from the primary markdown)
    wiki = _build_wiki_markdown(run_id, query, domain, created_at, summary, papers)
    wiki_path.write_text(wiki, encoding="utf-8")

    with sqlite3.connect(_db_path()) as conn:
        conn.execute(
            """
            INSERT INTO surveys
            (run_id, query, domain, created_at, summary, md_path, json_path, html_path, wiki_path)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                run_id,
                query,
                domain,
                created_at,
                summary,
                str(md_path),
                str(json_path),
                str(html_path),
                str(wiki_path),
            ),
        )
        for p in papers:
            conn.execute(
                """
                INSERT INTO papers
                (run_id, title, year, authors, abstract, citation_count, venue, url)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    run_id,
                    p.title,
                    p.year,
                    ", ".join(p.authors),
                    p.abstract,
                    p.citation_count,
                    p.venue,
                    p.url,
                ),
            )

    return {
        "md": str(md_path),
        "json": str(json_path),
        "html": str(html_path),
        "wiki": str(wiki_path),
        "db": str(_db_path()),
    }


def list_surveys(limit: int = 10) -> list[dict]:
    """Return recent surveys from the ledger."""
    init_db()
    with sqlite3.connect(_db_path()) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            "SELECT run_id, query, domain, created_at, summary FROM surveys ORDER BY created_at DESC LIMIT ?",
            (limit,),
        ).fetchall()
    return [dict(r) for r in rows]


def get_survey_content(run_id: str, fmt: str = "md") -> str | dict | None:
    """Load a saved survey output by run_id and format."""
    init_db()
    with sqlite3.connect(_db_path()) as conn:
        conn.row_factory = sqlite3.Row
        row = conn.execute(
            "SELECT md_path, json_path, html_path FROM surveys WHERE run_id = ?",
            (run_id,),
        ).fetchone()
    if not row:
        return None
    path_map = {
        "md": row["md_path"],
        "json": row["json_path"],
        "html": row["html_path"],
    }
    path = path_map.get(fmt)
    if not path or not Path(path).exists():
        return None
    text = Path(path).read_text(encoding="utf-8")
    if fmt == "json":
        return json.loads(text)
    return text
