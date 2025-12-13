# Contributing to Cursor Engineering Rules

Thank you for your interest in contributing! This document provides guidelines for contributing to this project.

---

## 🎯 How to Contribute

### 1. Report Issues

Found a bug or have a suggestion?

- **Check existing issues** first to avoid duplicates
- **Use issue templates** when available
- **Provide context**: What were you trying to do? What happened? What did you expect?
- **Include examples**: Code snippets, error messages, screenshots

### 2. Suggest New Rules

Want to add a new language, tool, or pattern?

**Before creating a new rule:**

- Check if it fits within an existing rule file
- Ensure it follows the project's structure and style
- Consider if it's broadly applicable (not too specific)

**Structure for new rules:**

```markdown
---
title: Clear, Descriptive Title
description: One-line summary of what this rule covers
priority: 100-999 (see priority guidelines below)
alwaysApply: true/false
files:
  include:
    - "**/*.ext"
---

# Rule Title

## Guiding Principle

One paragraph explaining the overall philosophy.

## Section 1

### Pattern Name

**Why:**
- Explanation

**Example:**
\```language
// Good example
\```

\```language
// Bad example (with explanation)
\```
```

### 3. Improve Existing Rules

Enhancement ideas:

- Add more examples
- Clarify confusing sections
- Add common mistakes/anti-patterns
- Update for newer tool versions
- Fix typos or formatting

### 4. Add Code Examples

High-quality examples should:

- ✅ Be production-ready (not toy examples)
- ✅ Show best practices
- ✅ Include error handling
- ✅ Be well-commented
- ✅ Follow the rule's standards

---

## 📝 Pull Request Process

### Before Submitting

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/your-feature-name`
3. **Make your changes**
4. **Test your changes**: Ensure examples work and formatting is correct
5. **Commit with conventional commits**: `feat: add rust async patterns`

### Commit Message Format

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

**Types:**

- `feat`: New feature or rule
- `fix`: Bug fix or correction
- `docs`: Documentation changes
- `refactor`: Code restructuring without behavior change
- `style`: Formatting, whitespace
- `test`: Adding tests
- `chore`: Maintenance tasks

**Examples:**

```
feat(python): add asyncio best practices
fix(terraform): correct state locking example
docs(readme): update installation instructions
refactor(go): reorganize concurrency section
```

### PR Guidelines

- **One PR per feature/fix**: Keep changes focused
- **Clear title and description**: Explain what and why
- **Reference issues**: Use `Fixes #123` or `Relates to #456`
- **Add examples**: Show before/after if applicable
- **Update INDEX.md**: If adding new rules

---

## 🏗️ Project Structure

```
cursor-engineering-rules/
├── rules/              # All .mdc rule files
│   ├── 050-workflow.mdc
│   ├── 100-core.mdc
│   ├── ...
│   └── INDEX.md       # Rule catalog
├── docs/              # Additional documentation
├── examples/          # Example configurations
├── README.md          # Main documentation
├── CONTRIBUTING.md    # This file
└── LICENSE            # MIT License
```

---

## 📋 Rule Numbering & Priority

### Numbering Scheme

Rules are numbered by category:

| Range | Category |
|-------|----------|
| 050-099 | Workflow & Process |
| 100-149 | Core & Version Control |
| 150-199 | Infrastructure as Code |
| 200-249 | Application Patterns |
| 250-299 | Cloud Platforms |
| 300-399 | Cross-Cutting Concerns |
| 800-899 | Documentation |
| 900-999 | Local Overrides |

### Priority Levels

- **Critical (alwaysApply: true)**: Core standards that apply to all projects
- **High (priority: 100-199)**: Language/tool-specific rules for primary stack
- **Medium (priority: 200-799)**: Supporting tools and patterns
- **Low (priority: 800-999)**: Documentation and utilities

---

## ✅ Code Quality Standards

### Rule File Standards

1. **YAML Frontmatter**: Include title, description, priority, alwaysApply, files
2. **Markdown Formatting**: Use headers, code blocks, lists consistently
3. **Code Examples**: Test examples work correctly
4. **Language**: Clear, concise, professional
5. **Length**: Balance comprehensiveness with readability

### Code Example Standards

```markdown
# ✅ GOOD - Clear, complete, explained
\```python
def calculate_total(items: list[Item]) -> Decimal:
    """Calculate total with proper error handling."""
    if not items:
        raise ValueError("Items list cannot be empty")
    
    return sum(item.price for item in items)
\```

# ❌ BAD - No error handling
\```python
def calculate_total(items):
    return sum(item.price for item in items)
\```
```

---

## 🧪 Testing Your Changes

### Validate Markdown

```bash
# Install markdownlint
npm install -g markdownlint-cli

# Check formatting
markdownlint rules/*.mdc
```

### Validate Code Examples

Ensure all code examples:

- Use correct syntax for the language
- Include necessary imports
- Follow the rule's own standards
- Are complete enough to understand

### Test in Cursor

1. Copy your rule to a test project
2. Configure `.cursorrules` to include it
3. Ask Cursor to generate code using the rule
4. Verify Cursor follows the patterns correctly

---

## 🌍 Internationalization

Currently, all rules are in English. If you'd like to contribute translations:

1. Create a new directory: `rules/i18n/<lang-code>/`
2. Translate rule files, keeping the same numbering
3. Update README.md with language selector

---

## 💡 Areas for Contribution

### High Priority

- [ ] Java best practices
- [ ] C# / .NET patterns
- [ ] Ruby on Rails patterns
- [ ] PHP modern patterns
- [ ] More cloud platform patterns (Oracle Cloud, IBM Cloud)
- [ ] Industry-specific patterns (fintech, healthcare, gaming)

### Medium Priority

- [ ] More testing patterns (property-based, contract, chaos)
- [ ] Performance benchmarking guides
- [ ] Database migration patterns
- [ ] CI/CD patterns for other platforms (GitLab, CircleCI, Jenkins)

### Nice to Have

- [ ] Video tutorials
- [ ] Interactive examples
- [ ] Rule validation tooling
- [ ] VS Code extension
- [ ] Migration guides (e.g., from other style guides)

---

## 📧 Questions?

- **GitHub Discussions**: For general questions and discussions
- **GitHub Issues**: For specific bugs or feature requests
- **Email**: [Your preferred contact method]

---

## 🙏 Code of Conduct

### Our Pledge

We are committed to providing a welcoming and inspiring community for all.

### Our Standards

**Positive behavior includes:**

- Using welcoming and inclusive language
- Being respectful of differing viewpoints
- Gracefully accepting constructive criticism
- Focusing on what is best for the community

**Unacceptable behavior includes:**

- Trolling, insulting/derogatory comments, and personal attacks
- Public or private harassment
- Publishing others' private information without permission
- Other conduct which could reasonably be considered inappropriate

### Enforcement

Instances of abusive, harassing, or otherwise unacceptable behavior may be reported by opening an issue or contacting the project maintainer.

---

## 📜 License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

**Thank you for contributing to Cursor Engineering Rules!** 🎉

Your contributions help developers worldwide write better, more maintainable code.
