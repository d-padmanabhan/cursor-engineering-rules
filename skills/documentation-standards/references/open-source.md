# Open Source Standards

## Essential Files

| File | Purpose |
|------|---------|
| `README.md` | Project overview and quick start |
| `LICENSE` | Legal terms |
| `CONTRIBUTING.md` | How to contribute |
| `CODE_OF_CONDUCT.md` | Community standards |
| `CHANGELOG.md` | Version history |
| `SECURITY.md` | Security policy |

## README Template

```markdown
# Project Name

![Build Status](badge-url)
![License](badge-url)
![Version](badge-url)

Short description of what this project does.

## Features

- ✨ Feature 1
- 🚀 Feature 2
- 🔒 Feature 3

## Installation

```bash
npm install project-name
```

## Usage

```javascript
import { thing } from 'project-name';
thing.doSomething();
```

## Documentation

See [docs](./docs) for detailed documentation.

## Contributing

See [CONTRIBUTING.md](./CONTRIBUTING.md).

## License

[MIT](./LICENSE)

```

## CONTRIBUTING.md Template

```markdown
# Contributing

Thank you for your interest in contributing!

## Getting Started

1. Fork the repository
2. Clone your fork
3. Create a feature branch

## Development

```bash
# Install dependencies
npm install

# Run tests
npm test

# Run linter
npm run lint
```

## Pull Request Process

1. Update documentation
2. Add tests for new features
3. Ensure all tests pass
4. Update CHANGELOG.md
5. Submit PR against `main`

## Code Style

- Follow existing patterns
- Run `npm run lint` before committing
- Write meaningful commit messages

## Reporting Issues

Use GitHub Issues. Include:

- Description of the problem
- Steps to reproduce
- Expected vs actual behavior
- Environment details

```

## License Selection

| License | Use When |
|---------|----------|
| MIT | Maximum permissiveness |
| Apache 2.0 | Patent protection needed |
| GPL 3.0 | Require derivative works to be open |
| BSD 3-Clause | Similar to MIT, explicit attribution |

## Security Policy

```markdown
# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 2.x.x   | ✅                 |
| 1.x.x   | ❌                 |

## Reporting a Vulnerability

Please report vulnerabilities to security@acme.com.

Do NOT open a public issue.

We will respond within 48 hours.
```

## Issue Templates

### Bug Report

```markdown
---
name: Bug Report
about: Report a bug
labels: bug
---

## Description
Clear description of the bug.

## Steps to Reproduce
1. Step one
2. Step two
3. Step three

## Expected Behavior
What should happen.

## Actual Behavior
What actually happens.

## Environment
- OS:
- Version:
- Node:
```

### Feature Request

```markdown
---
name: Feature Request
about: Suggest an idea
labels: enhancement
---

## Problem
Description of the problem.

## Proposed Solution
Your proposed solution.

## Alternatives Considered
Other approaches you considered.

## Additional Context
Any other context.
```

## PR Template

```markdown
## Description
Brief description of changes.

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Checklist
- [ ] Tests added
- [ ] Documentation updated
- [ ] CHANGELOG updated
- [ ] Linting passes
```
