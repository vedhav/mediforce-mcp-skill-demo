# wordtools-mcp

A minimal custom MCP server (stdio, FastMCP) used by the Word Explorer demo
workflow. Exposes one tool:

- **`anagrams(word)`** — dictionary words formable from the letters of `word`,
  read from `/usr/share/dict/words` (installed in the agent image).

Installed in the image via `pip install mcp/wordtools`, which puts the
`wordtools-mcp` console command on `PATH`. A workflow agent step references it:

```json
"mcpServers": [
  { "name": "wordtools", "command": "wordtools-mcp",
    "description": "anagrams(word) — words formable from a word's letters" }
]
```

Run locally:

```bash
pip install -e .
wordtools-mcp        # speaks MCP over stdio
```
