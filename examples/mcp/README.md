# MCP configuration examples

These files are **examples/templates** to help you configure MCP servers.

> [!IMPORTANT]
> These examples are **not authoritative** and may drift from upstream MCP server changes.
> Always review upstream docs and pin versions where you need repeatability.

## Files

- **`mcpServers.common.example.json`**: Common MCP servers (AWS + Cloudflare)
- **`mcpServers.github_remote.example.json`**: Optional GitHub remote MCP server example

## How to use the common MCP servers

This section shows how to use `mcpServers.common.example.json`.

### Cursor Agent

1. Open (or create) your project MCP config:

```bash
mkdir -p .cursor
code .cursor/mcp.json
```

1. Cursor expects a top-level `servers` object. Copy the server entries from `mcpServers.common.example.json`’s `mcpServers` object and paste them under `servers`.

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
> If you add more servers later, merge entries at the same level (don’t nest `servers` inside `servers`).

### Claude Desktop (optional)

If you use a client that expects `mcpServers` at the top level, you can usually paste the contents of `mcpServers.common.example.json` directly into that client’s config (or merge the keys under its existing `mcpServers` object).

## Optional: GitHub remote MCP server

If you want to add GitHub’s remote MCP server, use `mcpServers.github_remote.example.json` and provide `GITHUB_MCP_PAT` via environment variables.

## Environment variables

Some examples use environment variable placeholders.

- **AWS region**: set `AWS_REGION` (used by `iam-policy-autopilot`)
- **GitHub remote token**: set `GITHUB_MCP_PAT` (used only in the GitHub remote example)

> [!WARNING]
> Treat `GITHUB_MCP_PAT` as a secret. Do not commit it to git or paste it into JSON config files.

## Notes

- The AWS examples use `uvx` to run the servers. You’ll need Python tooling that provides `uvx`.
- The Cloudflare entries are HTTP MCP endpoints.
