# Cursor Engineering Rules MCP Server - Installation Guide

## Prerequisites

- **Node.js:** 20+ (check with `node --version`)
- **npm:** 10+ (check with `npm --version`)
- **Claude Desktop** or other MCP-compatible AI client

## Installation Steps

### 1. Install Dependencies

```bash
cd /path/to/cursor-engineering-rules/mcp/cursor-rules-mcp
npm install
```

### 2. Build the Server

```bash
npm run build
```

This compiles TypeScript to JavaScript in the `dist/` directory.

### 3. Link Globally (Optional)

To make the `cursor-rules-mcp` command available system-wide:

```bash
npm link
```

Verify installation:

```bash
which cursor-rules-mcp
# Should output: /usr/local/bin/cursor-rules-mcp (or similar)
```

### 4. Configure Claude Desktop

Edit Claude Desktop configuration file:

**macOS:**

```bash
code ~/Library/Application\ Support/Claude/claude_desktop_config.json
```

**Linux:**

```bash
code ~/.config/Claude/claude_desktop_config.json
```

**Windows:**

```bash
code %APPDATA%\Claude\claude_desktop_config.json
```

Add the MCP server configuration:

```json
{
  "mcpServers": {
    "cursor-engineering-rules": {
      "command": "cursor-rules-mcp",
      "env": {
        "CURSOR_RULES_PATH": "/path/to/cursor-engineering-rules/rules"
      }
    }
  }
}
```

**Note:** Adjust `CURSOR_RULES_PATH` to your actual path.

### 5. Restart Claude Desktop

Completely quit and restart Claude Desktop for the MCP server to load.

### 6. Verify Installation

In Claude Desktop, you should now see the Cursor Engineering Rules MCP server connected.

Try using the tools:

```
Can you list all available Cursor Engineering Rules?
```

Claude will use the `list_available_rules` tool.

```
Show me the Python engineering rules.
```

Claude will use `fetch_rule(category="languages", topic="python")`.

## Alternative: Run Without Global Install

If you don't want to use `npm link`, specify the full path in Claude Desktop config:

```json
{
  "mcpServers": {
    "cursor-engineering-rules": {
      "command": "node",
      "args": [
        "/path/to/cursor-engineering-rules/mcp/cursor-rules-mcp/dist/index.js"
      ],
      "env": {
        "CURSOR_RULES_PATH": "/path/to/cursor-engineering-rules/rules"
      }
    }
  }
}
```

## Troubleshooting

### MCP Server Not Showing Up

1. **Check Claude Desktop logs:**
   - macOS: `~/Library/Logs/Claude/`
   - Linux: `~/.config/Claude/logs/`
   - Windows: `%APPDATA%\Claude\logs\`

2. **Verify build succeeded:**

   ```bash
   ls -la /path/to/cursor-engineering-rules/mcp/cursor-rules-mcp/dist/
   ```

   Should show `index.js`, `server/`, `api/` directories.

3. **Test manually:**

   ```bash
   node /path/to/cursor-engineering-rules/mcp/cursor-rules-mcp/dist/index.js
   ```

   Server should start and log "Server connected and ready for requests"

### Permission Errors

```bash
sudo npm link
```

Or install without global link (see "Alternative" above).

### Rules Not Loading

Verify `CURSOR_RULES_PATH` points to the correct directory:

```bash
ls /path/to/cursor-engineering-rules/rules/
```

Should list `.mdc` files like `010-workflow.mdc`, `200-python.mdc`, etc.

## Development Mode

For active development with auto-rebuild:

```bash
# Terminal 1: Watch and rebuild
npm run watch

# Terminal 2: Run server with auto-restart
npm run dev
```

## Uninstall

```bash
# Remove global link
npm unlink cursor-rules-mcp

# Remove node_modules and build artifacts
cd /path/to/cursor-engineering-rules/mcp/cursor-rules-mcp
rm -rf node_modules dist

# Remove from Claude Desktop config
# Edit ~/Library/Application Support/Claude/claude_desktop_config.json
# Remove the "cursor-engineering-rules" entry
```

## Next Steps

Once installed, see [README.md](README.md) for:

- Available tools (`fetch_workflow_guide`, `fetch_rule`, `list_available_rules`)
- Rule categories and topics
- Usage examples

## Support

For issues:

1. Check Claude Desktop logs
2. Verify build artifacts exist (`dist/` directory)
3. Test server manually with `node dist/index.js`
4. Open an issue at [cursor-engineering-rules](https://github.com/d-padmanabhan/cursor-engineering-rules)
