# MCP Patterns

## Python MCP Server

```python
import asyncio
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

app = Server("my-server")

@app.list_tools()
async def list_tools():
    return [
        Tool(
            name="get_weather",
            description="Get current weather for a city",
            inputSchema={
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "City name"
                    }
                },
                "required": ["city"]
            }
        )
    ]

@app.call_tool()
async def call_tool(name: str, arguments: dict):
    if name == "get_weather":
        weather = await fetch_weather(arguments["city"])
        return [TextContent(type="text", text=f"Weather: {weather}")]
    raise ValueError(f"Unknown tool: {name}")

async def main():
    async with stdio_server() as (read, write):
        await app.run(read, write)

if __name__ == "__main__":
    asyncio.run(main())
```

## Configuration (Claude Desktop)

```json
{
  "mcpServers": {
    "my-server": {
      "command": "python",
      "args": ["/path/to/server.py"],
      "env": {
        "API_KEY": "xxx"
      }
    }
  }
}
```

## Tool Categories

### Data Retrieval

```typescript
{
  name: "search_database",
  description: "Search the database for records matching criteria",
  inputSchema: {
    type: "object",
    properties: {
      table: { type: "string" },
      filters: { type: "object" },
      limit: { type: "integer", default: 10 }
    }
  }
}
```

### Actions

```typescript
{
  name: "send_email",
  description: "Send an email. Use only when explicitly requested.",
  inputSchema: {
    type: "object",
    properties: {
      to: { type: "string", format: "email" },
      subject: { type: "string" },
      body: { type: "string" }
    },
    required: ["to", "subject", "body"]
  }
}
```

### File Operations

```typescript
{
  name: "read_file",
  description: "Read contents of a file",
  inputSchema: {
    type: "object",
    properties: {
      path: { type: "string", description: "File path relative to workspace" }
    },
    required: ["path"]
  }
}
```

## Prompts

```typescript
server.setRequestHandler("prompts/list", async () => ({
  prompts: [
    {
      name: "summarize",
      description: "Summarize a document",
      arguments: [
        {
          name: "url",
          description: "URL of the document",
          required: true
        }
      ]
    }
  ]
}));

server.setRequestHandler("prompts/get", async (request) => {
  const { name, arguments: args } = request.params;
  
  if (name === "summarize") {
    const content = await fetchDocument(args.url);
    return {
      messages: [
        {
          role: "user",
          content: {
            type: "text",
            text: `Please summarize the following document:\n\n${content}`
          }
        }
      ]
    };
  }
});
```

## Error Handling Patterns

```typescript
class ToolError extends Error {
  constructor(message: string, public code: string) {
    super(message);
  }
}

server.setRequestHandler("tools/call", async (request) => {
  try {
    const result = await executeTool(request.params);
    return { content: [{ type: "text", text: result }] };
  } catch (error) {
    if (error instanceof ToolError) {
      return {
        content: [{
          type: "text",
          text: JSON.stringify({
            error: error.code,
            message: error.message
          })
        }],
        isError: true
      };
    }
    // Unexpected error
    console.error(error);
    return {
      content: [{ type: "text", text: "Internal server error" }],
      isError: true
    };
  }
});
```

## Testing MCP Servers

```typescript
import { Client } from "@modelcontextprotocol/sdk/client/index.js";

describe("MCP Server", () => {
  let client: Client;
  
  beforeEach(async () => {
    client = new Client({ name: "test" }, {});
    await client.connect(transport);
  });
  
  it("should list tools", async () => {
    const result = await client.listTools();
    expect(result.tools).toHaveLength(1);
    expect(result.tools[0].name).toBe("get_weather");
  });
  
  it("should call tool", async () => {
    const result = await client.callTool({
      name: "get_weather",
      arguments: { city: "London" }
    });
    expect(result.content[0].text).toContain("London");
  });
});
```
