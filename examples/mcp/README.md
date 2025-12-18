# MCP configuration examples

These files are **examples/templates** to help you configure MCP servers.

> [!IMPORTANT]
> These examples are **not authoritative** and may drift from upstream MCP server changes.
> Always review upstream docs and pin versions where you need repeatability.

## Files

- **`claude_desktop_config.common.example.json`**: A starter `mcpServers` block for common servers (AWS + Cloudflare)
- **`claude_desktop_config.github_remote.example.json`**: A separate example for the GitHub remote MCP server

## How to use (Cursor Agent)

1. Open (or create) your Cursor MCP config:

```bash
mkdir -p .cursor
code .cursor/mcp.json
```

1. Cursor expects a top-level `servers` object. Take the entries under each example file’s `mcpServers` object and paste them under `servers`.

Example:

```json
{
  "servers": {
    "aws-docs": {
      "type": "stdio",
      "command": "uvx",
      "args": ["awslabs.aws-documentation-mcp-server@latest"]
    }
  }
}
```

> [!TIP]
> If you copy/paste multiple examples, merge server entries at the same level (don’t nest `servers` inside `servers`).

## Environment variables

Some examples use environment variable placeholders.

- **AWS region**: set `AWS_REGION` (used by `iam-policy-autopilot`)
- **GitHub remote token**: set `GITHUB_MCP_PAT` (used only in the GitHub remote example)

> [!WARNING]
> Treat `GITHUB_MCP_PAT` as a secret. Do not commit it to git or paste it into JSON config files.

## Notes

- The AWS examples use `uvx` to run the servers. You’ll need Python tooling that provides `uvx`.
- The Cloudflare entries are HTTP MCP endpoints.
