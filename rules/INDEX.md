# Cursor Rules Index

Quick lookup table for all cursor rules files.

## Core Rules (000-099)

| File | Description | Priority | Always Apply |
|------|-------------|----------|--------------|
| [050-workflow.mdc](050-workflow.mdc) | Workflow orchestration (Plan/Implement/Review) | 50 | Context-aware |
| [100-core.mdc](100-core.mdc) | Core coding standards and best practices | 100 | Yes |
| [110-git.mdc](110-git.mdc) | Git standards and workflows | 110 | Context-aware |

## Language Standards (100-199)

| File | Description | Priority | Always Apply |
|------|-------------|----------|--------------|
| [115-utilities.mdc](115-utilities.mdc) | Command-line utilities (lynx, curl, jq, httpie) | 115 | No |
| [120-gha.mdc](120-gha.mdc) | GitHub Actions workflows and CI/CD | 120 | No |
| [130-bash.mdc](130-bash.mdc) | Bash scripting standards | 130 | No |
| [140-terraform.mdc](140-terraform.mdc) | Terraform Infrastructure as Code | 140 | No |
| [150-cloudformation.mdc](150-cloudformation.mdc) | AWS CloudFormation standards | 150 | No |
| [155-docker.mdc](155-docker.mdc) | Docker & container best practices | 155 | No |
| [160-python.mdc](160-python.mdc) | Python development standards | 160 | No |
| [165-typescript.mdc](165-typescript.mdc) | TypeScript patterns and type safety | 165 | No |
| [170-javascript.mdc](170-javascript.mdc) | JavaScript/Node.js standards | 170 | No |
| [180-go.mdc](180-go.mdc) | Go programming standards | 180 | No |
| [190-makefile.mdc](190-makefile.mdc) | Makefile patterns | 190 | No |

## Development Tools (200-299)

| File | Description | Priority | Always Apply |
|------|-------------|----------|--------------|
| [200-cli.mdc](200-cli.mdc) | CLI application patterns | 200 | No |
| [210-open-source.mdc](210-open-source.mdc) | Open source project patterns | 210 | No |
| [220-documentation.mdc](220-documentation.mdc) | Documentation engineering | 220 | No |
| [230-mcp-servers.mdc](230-mcp-servers.mdc) | MCP server patterns | 230 | No |
| [240-configuration.mdc](240-configuration.mdc) | Configuration management | 240 | No |

## Cloud & Infrastructure (250-299)

| File | Description | Priority | Always Apply |
|------|-------------|----------|--------------|
| [250-cloudflare.mdc](250-cloudflare.mdc) | Cloudflare rules and Workers | 250 | No |
| [260-kubernetes.mdc](260-kubernetes.mdc) | Kubernetes & EKS patterns | 260 | No |
| [270-postgresql.mdc](270-postgresql.mdc) | PostgreSQL database patterns | 270 | No |
| [280-aws.mdc](280-aws.mdc) | AWS platform engineering | 280 | No |

## Testing & Security (300-399)

| File | Description | Priority | Always Apply |
|------|-------------|----------|--------------|
| [300-testing.mdc](300-testing.mdc) | Testing strategies (Unit/Integration/E2E) | 300 | No |
| [310-security.mdc](310-security.mdc) | Security best practices & OWASP Top 10 | 310 | Yes |

## Documentation Standards (800-899)

| File | Description | Priority | Always Apply |
|------|-------------|----------|--------------|
| [800-markdown.mdc](800-markdown.mdc) | Markdown & Mermaid diagramming | 800 | Yes |

## Local Overrides (900-999)

| File | Description | Priority | Always Apply |
|------|-------------|----------|--------------|
| [999-local-overrides.mdc](999-local-overrides.mdc) | Workspace-specific overrides | 999 | No |

---

## Quick Reference by Technology

### Languages
- **Bash**: [130-bash.mdc](130-bash.mdc)
- **Go**: [180-go.mdc](180-go.mdc)
- **JavaScript**: [170-javascript.mdc](170-javascript.mdc)
- **Python**: [160-python.mdc](160-python.mdc)
- **TypeScript**: [165-typescript.mdc](165-typescript.mdc)

### Infrastructure as Code
- **CloudFormation**: [150-cloudformation.mdc](150-cloudformation.mdc)
- **Terraform**: [140-terraform.mdc](140-terraform.mdc)

### Cloud Platforms
- **AWS**: [280-aws.mdc](280-aws.mdc)
- **Cloudflare**: [250-cloudflare.mdc](250-cloudflare.mdc)

### Container & Orchestration
- **Docker**: [155-docker.mdc](155-docker.mdc)
- **Kubernetes**: [260-kubernetes.mdc](260-kubernetes.mdc)

### CI/CD & Testing
- **GitHub Actions**: [120-gha.mdc](120-gha.mdc)
- **Testing**: [300-testing.mdc](300-testing.mdc)

### Security
- **Security Best Practices**: [310-security.mdc](310-security.mdc)

### Databases
- **PostgreSQL**: [270-postgresql.mdc](270-postgresql.mdc)

### Utilities
- **Command-Line Tools**: [115-utilities.mdc](115-utilities.mdc) (lynx, curl, jq, httpie)

### Documentation
- **Markdown & Diagrams**: [800-markdown.mdc](800-markdown.mdc)
- **Documentation Engineering**: [220-documentation.mdc](220-documentation.mdc)

### Development Patterns
- **CLI Applications**: [200-cli.mdc](200-cli.mdc)
- **Configuration**: [240-configuration.mdc](240-configuration.mdc)
- **MCP Servers**: [230-mcp-servers.mdc](230-mcp-servers.mdc)
- **Makefile**: [190-makefile.mdc](190-makefile.mdc)
- **Open Source**: [210-open-source.mdc](210-open-source.mdc)

---

## Files Marked "Always Apply"

These rules are automatically applied to all projects:

1. **[100-core.mdc](100-core.mdc)** - Core coding standards
2. **[310-security.mdc](310-security.mdc)** - Security best practices
3. **[800-markdown.mdc](800-markdown.mdc)** - Markdown standards

---

## Setup & Configuration

- **[README.md](README.md)** - Overview and quick start
- **[NEW_REPO_CHECKLIST.md](NEW_REPO_CHECKLIST.md)** - Step-by-step checklist
- **[SETUP_GUIDE.md](SETUP_GUIDE.md)** - Complete setup guide
- **[CHANGELOG.md](CHANGELOG.md)** - Version history
- **[setup-workspace.sh](setup-workspace.sh)** - Setup script
- **[setup-all-repos.sh](setup-all-repos.sh)** - Batch setup script

---

**Last Updated**: December 2025  
**Total Rules**: 23 files  
**Lines of Code**: ~11,716 lines
