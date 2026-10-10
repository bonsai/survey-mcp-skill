# survey-mcp-skill

Conversational local survey agent built with FastAPI + FastMCP + OpenAPI.

## Features

- Talk to it: natural-language query → survey
- Paper survey via Semantic Scholar
- Outputs: SQLite ledger, Markdown, JSON, HTML, and llm-wiki recap
- Runs locally; no AWS

## Setup

```bash
cd ~/.skills/survey-mcp-skill
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

## Run

stdio (for Pi MCP):

```bash
python -m survey_mcp_skill stdio
```

HTTP (with OpenAPI docs):

```bash
python -m survey_mcp_skill http --port 8765
```

## MCP registration

```bash
pi mcp add survey-mcp-skill -- \
  /home/sexy/.skills/survey-mcp-skill/.venv/bin/python \
  -m survey_mcp_skill stdio
```

## Output locations

- DB: `~/.db/survey_mcp_skill.db`
- Reports: `~/data-survey-mcp-skill/YYYY-MM-DD/`
- Wiki recaps: `~/llm-wiki/survey-mcp-skill/`
