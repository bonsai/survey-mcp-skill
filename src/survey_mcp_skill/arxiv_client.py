"""Minimal arXiv API client (fallback when Semantic Scholar rate-limits)."""

import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime


ARXIV_NS = {"atom": "http://www.w3.org/2005/Atom", "arxiv": "http://arxiv.org/schemas/atom"}


def search_arxiv(query: str, limit: int = 10) -> list[dict]:
    """Search arXiv and return a list of paper dicts."""
    encoded = urllib.parse.quote(query)
    url = f"http://export.arxiv.org/api/query?search_query=all:{encoded}&start=0&max_results={limit}&sortBy=relevance&sortOrder=descending"
    with urllib.request.urlopen(url, timeout=30.0) as resp:
        xml_text = resp.read().decode("utf-8")

    root = ET.fromstring(xml_text)
    results: list[dict] = []
    for entry in root.findall("atom:entry", ARXIV_NS):
        title = entry.findtext("atom:title", default="", namespaces=ARXIV_NS).replace("\n", " ").strip()
        summary = entry.findtext("atom:summary", default="", namespaces=ARXIV_NS).strip()
        published = entry.findtext("atom:published", default="", namespaces=ARXIV_NS)
        year: int | None = None
        if published:
            try:
                year = datetime.fromisoformat(published.replace("Z", "+00:00")).year
            except Exception:
                pass
        authors = [
            a.findtext("atom:name", default="", namespaces=ARXIV_NS).strip()
            for a in entry.findall("atom:author", ARXIV_NS)
        ]
        link = entry.find("atom:link[@rel='alternate']", ARXIV_NS)
        url = link.get("href") if link is not None else None
        results.append(
            {
                "title": title,
                "authors": [{"name": n} for n in authors],
                "year": year,
                "abstract": summary,
                "citationCount": None,
                "venue": "arXiv",
                "url": url,
            }
        )
    return results
