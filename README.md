# Cursor Engineering Rules

> **Production-grade Cursor rules for 15+ languages and cloud platforms**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Comprehensive, battle-tested Cursor IDE rules for professional software engineering. Curated `.mdc` files covering languages, cloud platforms, DevOps tools, and engineering patterns.

---

## What's Included

### Core Standards

- **[100-core.mdc](rules/100-core.mdc)** - Core coding standards and review guidelines
- **[050-workflow.mdc](rules/050-workflow.mdc)** - Development workflow patterns
- **[110-git.mdc](rules/110-git.mdc)** - Git conventions and commit standards

### Programming Languages

- **[160-python.mdc](rules/160-python.mdc)** - Python best practices (PEP 8, type hints, async)
- **[180-go.mdc](rules/180-go.mdc)** - Go patterns (error handling, concurrency, generics)
- **[170-javascript.mdc](rules/170-javascript.mdc)** - JavaScript/Node.js (ES modules, async/await)
- **[165-typescript.mdc](rules/165-typescript.mdc)** - TypeScript (type safety, advanced types)
- **[185-rust.mdc](rules/185-rust.mdc)** - Rust (ownership, borrowing, async)
- **[130-bash.mdc](rules/130-bash.mdc)** - Shell scripting (POSIX compliance, safety)

### Cloud Platforms

- **[280-aws.mdc](rules/280-aws.mdc)** - AWS (EKS, VPC Lattice, Zero Trust, IAM)
- **[285-azure.mdc](rules/285-azure.mdc)** - Azure (Bicep, Key Vault, App Service)
- **[290-gcp.mdc](rules/290-gcp.mdc)** - GCP (Cloud Run, GKE, Secret Manager)
- **[250-cloudflare.mdc](rules/250-cloudflare.mdc)** - Cloudflare (Workers, Rules Engine)

### AI & Machine Learning

- **[295-ai-ml.mdc](rules/295-ai-ml.mdc)** - LLM integration (OpenAI, Claude, Bedrock, Vertex AI)
- **[230-mcp-servers.mdc](rules/230-mcp-servers.mdc)** - Model Context Protocol servers

### DevOps & Infrastructure

- **[140-terraform.mdc](rules/140-terraform.mdc)** - Terraform (modules, state, validation)
- **[150-cloudformation.mdc](rules/150-cloudformation.mdc)** - CloudFormation templates
- **[260-kubernetes.mdc](rules/260-kubernetes.mdc)** - Kubernetes & EKS patterns
- **[120-gha.mdc](rules/120-gha.mdc)** - GitHub Actions (workflows, security, OIDC)
- **[145-ansible.mdc](rules/145-ansible.mdc)** - Ansible (playbooks, roles, idempotency)
- **[195-helm.mdc](rules/195-helm.mdc)** - Helm charts and templating
- **[155-docker.mdc](rules/155-docker.mdc)** - Docker & containers (multi-stage builds, security)

### Security & Testing

- **[310-security.mdc](rules/310-security.mdc)** - OWASP Top 10, secret management
- **[300-testing.mdc](rules/300-testing.mdc)** - Unit/Integration/E2E testing strategies

### Patterns & Best Practices

- **[320-api-design.mdc](rules/320-api-design.mdc)** - REST API design patterns
- **[330-observability.mdc](rules/330-observability.mdc)** - Logging, metrics, tracing
- **[270-postgresql.mdc](rules/270-postgresql.mdc)** - PostgreSQL patterns
- **[220-documentation.mdc](rules/220-documentation.mdc)** - Documentation standards
- **[210-open-source.mdc](rules/210-open-source.mdc)** - Open source project patterns
- **[200-cli.mdc](rules/200-cli.mdc)** - CLI application patterns
- **[190-makefile.mdc](rules/190-makefile.mdc)** - Makefile patterns
- **[240-configuration.mdc](rules/240-configuration.mdc)** - Configuration management

### Utilities

- **[115-utilities.mdc](rules/115-utilities.mdc)** - CLI utilities (lynx, curl, jq, ripgrep)
- **[800-markdown.mdc](rules/800-markdown.mdc)** - Markdown & Mermaid diagrams

---

## MCP Server

Model Context Protocol (MCP) server for Cursor and other MCP-compatible AI clients.

```bash
# Install
cd mcp/cursor-rules-mcp
npm install
npm run build
npm link

# Configure Claude Desktop
# Add to ~/Library/Application Support/Claude/claude_desktop_config.json:
{
  "mcpServers": {
    "cursor-engineering-rules": {
      "command": "cursor-rules-mcp"
    }
  }
}
```

**Features:**

- Fetch workflow guide (Plan/Implement/Review)
- Fetch specific rules by category/topic
- List all available rules
- Just-in-time rule loading (load only what you need)

See [mcp/cursor-rules-mcp/README.md](mcp/cursor-rules-mcp/README.md) for full documentation.

---

## Quick Start

### Option 1: Use Individual Rules

Copy specific rules to your project:

```bash
# Create Cursor rules directory
mkdir -p .cursor/rules

# Copy specific rules you need
cp path/to/cursor-engineering-rules/rules/160-python.mdc .cursor/rules/
cp path/to/cursor-engineering-rules/rules/280-aws.mdc .cursor/rules/

# (Optional) Copy workflow templates (tasks, active-context, etc.)
mkdir -p .cursor/rules/templates
cp path/to/cursor-engineering-rules/rules/templates/*.template .cursor/rules/templates/
```

### Option 1.5: Use Setup Scripts (Convenience)

If you keep a shared checkout of this repo, you can bootstrap a workspace with:

```bash
/path/to/cursor-engineering-rules/setup-workspace.sh -S -l .
```

Add to your `.cursorrules` file:

```yaml
rules:
  - .cursor/rules/160-python.mdc
  - .cursor/rules/280-aws.mdc
```

### Option 2: Use All Rules (Recommended)

Symlink the entire rules directory:

```bash
# From your project root
ln -s /absolute/path/to/cursor-engineering-rules/rules .cursor/rules
```

Configure `.cursorrules`:

```yaml
# Load all rules
rulesDirectory: .cursor/rules

# Or be selective with alwaysApply rules
rules:
  - .cursor/rules/100-core.mdc
  - .cursor/rules/160-python.mdc
  - .cursor/rules/310-security.mdc
```

### Option 3: Cherry-Pick by Technology

Create a custom `.cursorrules` that includes only relevant rules:

```yaml
# Python + AWS project
rules:
  - .cursor/rules/100-core.mdc
  - .cursor/rules/110-git.mdc
  - .cursor/rules/160-python.mdc
  - .cursor/rules/280-aws.mdc
  - .cursor/rules/140-terraform.mdc
  - .cursor/rules/310-security.mdc
  - .cursor/rules/300-testing.mdc
```

---

## Rule Priorities

Rules have `alwaysApply` flags and priority levels:

- **Always Apply**: Core standards (100-core, 110-git, 310-security)
- **High Priority**: Language-specific rules for your stack
- **Medium Priority**: Platform/tool-specific rules
- **Low Priority**: Documentation and utility guides

See [rules/INDEX.md](rules/INDEX.md) for complete categorization.

---

## Features

### Production Quality

- **Battle-tested** patterns from real-world projects
- **Security-first** approach (OWASP Top 10, secret scanning)
- **Performance-focused** (benchmarks, optimization patterns)

### Comprehensive Coverage

- **9 programming languages** (Python, Go, TypeScript, JavaScript, Rust, Bash, SQL, etc.)
- **4 major cloud platforms** (AWS, Azure, GCP, Cloudflare)
- **15+ DevOps tools** (Terraform, K8s, Docker, Ansible, Helm, GitHub Actions)
- **AI/ML integration** (OpenAI, Claude, Bedrock, Vertex AI)

### Code Examples

- **Real-world examples** for every pattern
- **Good vs Bad** comparisons
- **Common mistakes** and anti-patterns
- **Quick reference** sections

### Modern Standards

- **Latest versions** (Python 3.12+, Go 1.23+, Node 20+)
- **Modern patterns** (async/await, generics, type safety)
- **Current tools** (ripgrep, jq, httpie)

---

## Customization

### Workspace-Specific Overrides

Use `999-local-overrides.mdc` for project-specific rules:

```bash
# Copy to your project
cp rules/999-local-overrides.mdc .cursor/rules/999-local-overrides.mdc

# Edit to add project-specific rules
vim .cursor/rules/999-local-overrides.mdc
```

### Creating Custom Rules

Follow the standard format:

```markdown
---
title: My Custom Rule
description: Project-specific patterns
priority: 900
alwaysApply: false
files:
  include:
    - "**/*.py"
---

# My Custom Rule

## Pattern 1
[Your custom patterns here]
```

---

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Areas for Contribution

- Additional language support (Java, C#, Ruby, PHP)
- More cloud platform patterns
- Industry-specific patterns (fintech, healthcare, etc.)
- Performance benchmarks
- Additional code examples

---

## License

MIT License - see [LICENSE](LICENSE) for details.

---

## Acknowledgments

This project was inspired by and incorporates patterns from:

- **AI Developer Guide**: <https://github.com/dwmkerr/ai-developer-guide> - Workflow patterns and context management
- **Cursor Memory Bank**: <https://github.com/vanzan01/cursor-memory-bank> - Context file management patterns

---

## Related Projects

- [eslint-config-airbnb](https://github.com/airbnb/javascript) - JavaScript style guide
- [google-styleguides](https://github.com/google/styleguide) - Google's style guides
- [uber-go-guide](https://github.com/uber-go/guide) - Uber's Go style guide
