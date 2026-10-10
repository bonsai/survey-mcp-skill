# survey-mcp-skill

話しかけるだけで論文サーベイを実行し、結果を DB / Markdown / JSON / HTML / llm-wiki に出力する MCP skill。

FastAPI + FastMCP + OpenAPI で実装。ローカル実行、AWS 不使用。

## 提供ツール

- `run_survey` — クエリから survey を実行
- `list_surveys` — 過去の survey 一覧
- `get_survey` — 指定 survey の結果を取得

## 使い方

ユーザーが「〜についてサーベイして」などと言ったら、`run_survey` を呼ぶ。

```json
{
  "query": "large language model reasoning",
  "domain": "paper",
  "max_papers": 10
}
```

結果はローカルに保存され、ファイルパスが返る。

## ローカル実行

```bash
cd ~/.skills/survey-mcp-skill
source .venv/bin/activate

# stdio MCP for pi
python -m survey_mcp_skill stdio

# HTTP + OpenAPI docs
python -m survey_mcp_skill http --port 8765
```

OpenAPI docs: http://127.0.0.1:8765/docs
