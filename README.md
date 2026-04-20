# ink-mcp-server

An MCP server that wraps the [Ink](https://pdf-annotator-ink.fly.dev) PDF annotation API, exposing it as the `annotate_pdf` tool for Claude and other MCP clients.

## Tools

### `annotate_pdf`

Annotate a PDF with AI-powered highlights, margin notes, and symbols.

**Inputs:**
- `pdf_b64` (string, required) — Base64-encoded PDF bytes
- `document_title` (string, optional) — Title of the document
- `anthropic_api_key` (string, optional) — Override the server-level Anthropic API key

**Output:**
```json
{
  "pdf_b64": "<base64-encoded annotated PDF>",
  "stats": {
    "pages": 5,
    "highlights": 12,
    "notes": 8,
    "symbols": 3
  }
}
```

## Environment variables

| Variable | Default | Description |
|---|---|---|
| `INK_API_URL` | `https://pdf-annotator-ink.fly.dev` | Base URL of the Ink API |
| `ANTHROPIC_API_KEY` | *(none)* | Forwarded as `x-anthropic-api-key` to the Ink API |

## Local setup

```bash
pip install -r requirements.txt
```

### Test with MCP Inspector

```bash
mcp dev server.py
```

This opens the MCP Inspector UI in your browser. Select the `annotate_pdf` tool and call it with a base64-encoded PDF to verify everything works.

### Test with Claude Desktop

Add to `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "ink": {
      "command": "python",
      "args": ["/path/to/ink-mcp-server/server.py"],
      "env": {
        "ANTHROPIC_API_KEY": "sk-ant-..."
      }
    }
  }
}
```

## Fly.io deployment

MCP stdio servers run as [Fly Machines](https://fly.io/docs/machines/) (not HTTP services).

```bash
# First deploy
fly launch --no-deploy --copy-config
fly secrets set ANTHROPIC_API_KEY=sk-ant-...
fly deploy

# Connect from an MCP client
fly machine exec ink-mcp-server python server.py
```

The `fly.toml` intentionally has no `[http_service]` block — this server communicates over stdin/stdout only.
