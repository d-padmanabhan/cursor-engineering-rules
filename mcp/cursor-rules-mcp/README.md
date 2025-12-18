# Cursor Engineering Rules MCP Server

**Model Context Protocol (MCP) server for Cursor Engineering Rules** - Production-grade AI agent rules for 15+ languages, multi-cloud infrastructure, and DevOps.

## Features

- **35+ Engineering Rules** covering languages, infrastructure, cloud platforms, and DevOps
- **15+ Languages:** Python, Go, Rust, TypeScript, JavaScript, Bash, and more
- **Multi-Cloud:** AWS, Azure, GCP, Cloudflare
- **Infrastructure as Code:** Terraform, CloudFormation, Kubernetes, Docker, Ansible, Helm
- **Production-Grade:** Security (OWASP), testing, observability, API design
- **Workflow Philosophy:** Plan/Implement/Review with Golden Rules

## Installation

### Prerequisites

- Node.js 20+
- npm or yarn

### Install from npm (when published)

```bash
npm install -g cursor-engineering-rules-mcp
```

### Install from source

```bash
cd mcp/cursor-rules-mcp
npm install
npm run build
npm link
```

## Configuration

### Claude Desktop

Add to `~/Library/Application Support/Claude/claude_desktop_config.json`:

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

### Cursor

Add to `.cursor/mcp.json`:

```json
{
  "servers": {
    "cursor-engineering-rules": {
      "command": "cursor-rules-mcp",
      "env": {
        "CURSOR_RULES_PATH": "/path/to/cursor-engineering-rules/rules"
      }
    }
  }
}
```

### Environment Variables

- `CURSOR_RULES_PATH`: Optional path to rules directory (defaults to bundled rules)

## Usage

The MCP server provides three tools:

### 1. `fetch_workflow_guide`

Fetch the core workflow guide (Plan/Implement/Review with Golden Rules). **Essential reading for all AI agents.**

```typescript
// No arguments required
fetch_workflow_guide()
```

### 2. `fetch_rule`

Fetch a specific engineering rule.

```typescript
// Example: Fetch Python rules
fetch_rule({
  category: "languages",
  topic: "python"
})

// Example: Fetch AWS rules
fetch_rule({
  category: "cloud",
  topic: "aws"
})

// Example: Fetch Terraform rules
fetch_rule({
  category: "infrastructure",
  topic: "terraform"
})
```

**Available Categories:**

- `core`: workflow, core-principles, git, utilities
- `languages`: python, go, rust, typescript, javascript, bash
- `infrastructure`: terraform, cloudformation, docker, kubernetes, ansible, helm
- `cloud`: aws, azure, gcp, cloudflare
- `devops`: github-actions, makefile, cli
- `patterns`: documentation, mcp-servers, configuration, open-source, testing, security, api-design, observability
- `databases`: postgresql
- `other`: ai-ml, markdown

### 3. `list_available_rules`

List all available engineering rules with categories, descriptions, and priorities.

```typescript
// No arguments required
list_available_rules()
```

## Example Workflow

1. **Start by reading the workflow guide:**

   ```typescript
   fetch_workflow_guide()
   ```

2. **List all available rules:**

   ```typescript
   list_available_rules()
   ```

3. **Fetch specific rules as needed:**

   ```typescript
   // Working on Python?
   fetch_rule({ category: "languages", topic: "python" })
   
   // Deploying to AWS?
   fetch_rule({ category: "cloud", topic: "aws" })
   
   // Writing Terraform?
   fetch_rule({ category: "infrastructure", topic: "terraform" })
   ```

## Rule Categories

### Core (Priority 50-115)

- **Workflow** (50): Plan/Implement/Review approach with Golden Rules
- **Core Principles** (100): SOLID, DRY, KISS, YAGNI, Fail Fast
- **Git** (110): Conventional commits, branching, commit approval
- **Utilities** (115): Ripgrep, fzf, jq, yq, CLI tools

### Languages (Priority 130-185)

- **Bash** (130): POSIX compliance, ShellCheck, safety patterns
- **Python** (160): Python 3.12+, type hints, AWS Lambda patterns
- **TypeScript** (165): Strict mode, ESM, modern patterns
- **JavaScript** (170): ES modules, async/await, Node.js
- **Go** (180): Idiomatic Go, error handling, concurrency
- **Rust** (185): Ownership, lifetimes, async patterns

### Infrastructure (Priority 140-260)

- **Terraform** (140): Modules, state management, workspaces
- **Ansible** (145): Playbooks, roles, idempotency
- **CloudFormation** (150): Templates, stacks, nested stacks
- **Docker** (155): Multi-stage builds, security, optimization
- **Helm** (195): Charts, templating, releases
- **Kubernetes** (260): Manifests, operators, CRDs, security

### Cloud (Priority 250-290)

- **Cloudflare** (250): Workers, Rules Engine, DNS, security
- **AWS** (280): EKS, VPC Lattice, Lambda, IAM
- **Azure** (285): Bicep, Key Vault, App Service
- **GCP** (290): GKE, Cloud Run, Secret Manager

### DevOps (Priority 120-200)

- **GitHub Actions** (120): Workflows, OIDC, security
- **Makefile** (190): Phony targets, recipes, conventions
- **CLI** (200): argparse, typer, rich, user experience

### Patterns (Priority 210-330)

- **Open Source** (210): Contributing, licensing, community
- **Documentation** (220): MkDocs, Docusaurus, API docs
- **MCP Servers** (230): Model Context Protocol patterns
- **Configuration** (240): Config management, secrets
- **Testing** (300): Unit, integration, E2E testing
- **Security** (310): OWASP, secrets, IAM, least privilege
- **API Design** (320): REST, GraphQL, gRPC patterns
- **Observability** (330): Logging, metrics, tracing

### Databases (Priority 270)

- **PostgreSQL** (270): Performance, replication, security

### Other (Priority 295-800)

- **AI/ML** (295): Machine learning patterns
- **Markdown** (800): GFM, Mermaid diagrams

## Development

```bash
# Install dependencies
npm install

# Build
npm run build

# Watch mode
npm run watch

# Run locally
npm start
```

## Architecture

```
mcp/cursor-rules-mcp/
 src/
    api/
       client.ts          # API client for reading rules
    server/
       mcp-server.ts      # MCP server implementation
    index.ts               # Entry point
 package.json
 tsconfig.json
 README.md
```

## Comparison with AI Developer Guide

| Feature | AI Developer Guide | Cursor Engineering Rules |
|---------|-------------------|--------------------------|
| **Focus** | Workflow philosophy | Production standards |
| **Languages** | 3 (Python, Go, Shell) | 15+ |
| **Cloud Platforms** | 0 | 4 (AWS, Azure, GCP, Cloudflare) |
| **Infrastructure** | Basic | Comprehensive (Terraform, K8s, Docker, etc.) |
| **Security** | Basic | OWASP, IAM, secrets, compliance |
| **Best For** | Startups, teaching | Enterprise, production systems |

**Cursor Engineering Rules v2** combines both: workflow philosophy from AI Developer Guide + comprehensive production standards.

## Resources

- [Cursor Engineering Rules Repository](https://github.com/d-padmanabhan/cursor-engineering-rules)
- [MCP Specification](https://spec.modelcontextprotocol.io/)
- [MCP Registry](https://github.com/modelcontextprotocol/registry)
- [MCP SDK](https://github.com/modelcontextprotocol/sdk)

## License

MIT

## Author

Platform Engineering Team

## Credits

- **Workflow Philosophy:** Inspired by [AI Developer Guide](https://github.com/dwmkerr/ai-developer-guide)
- **Technical Standards:** Comprehensive production-grade rules for enterprise engineering
