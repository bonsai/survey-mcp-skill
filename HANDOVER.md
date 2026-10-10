# HANDOVER

## Current status

- Skill `survey-mcp-skill` implemented with FastAPI + FastMCP + OpenAPI.
- Three MCP tools exposed: `run_survey`, `list_surveys`, `get_survey`.
- Registered in Pi via `~/.pi/agent/mcp.json` with `direct` exposure.
- Paper domain uses Semantic Scholar (primary) with arXiv fallback on 429.
- Outputs: SQLite (`~/.db/survey_mcp_skill.db`), MD/JSON/HTML (`~/data-survey-mcp-skill/`), llm-wiki recaps (`~/llm-wiki/survey-mcp-skill/`).
- End-to-end tested with `fastapi.testclient.TestClient` and live Pi `mcp list`.

## Next steps

1. Add Semantic Scholar API key support to avoid 429 fallback.
2. Implement `repo` and `marketing` domains with plugin recipes.
3. Add scoring / evaluation gate and gap discovery inspired by `survey-wisdom-core`.
4. Write unit tests.
5. Consider auto-open browser for HTML reports.
