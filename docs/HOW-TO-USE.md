# How to Use Cursor Engineering Rules

This guide explains how to integrate Cursor Engineering Rules into your projects.

---

## 📋 Table of Contents

1. [Installation Methods](#installation-methods)
2. [Configuration Strategies](#configuration-strategies)
3. [Rule Selection Guide](#rule-selection-guide)
4. [Testing Your Setup](#testing-your-setup)
5. [Troubleshooting](#troubleshooting)
6. [Advanced Usage](#advanced-usage)

---

## Installation Methods

### Method 1: Symlink (Recommended for Multiple Projects)

**Advantages:**
- Update rules once, all projects benefit
- No duplication
- Easy maintenance

**Setup:**

```bash
# Clone the repository
git clone https://github.com/d-padmanabhan/cursor-engineering-rules.git
cd /path/to/your/workspace

# From your project
cd /path/to/your/project
mkdir -p .cursor
ln -s /absolute/path/to/cursor-engineering-rules/rules .cursor/rules

# Verify
ls -la .cursor/rules
```

**Configure `.cursorrules`:**

```yaml
rulesDirectory: .cursor/rules
```

---

### Method 2: Copy Rules (Recommended for Single Project)

**Advantages:**
- Self-contained project
- Version control rules with project
- Custom modifications per project

**Setup:**

```bash
# From your project
cd /path/to/your/project
mkdir -p .cursor/rules

# Copy all rules
cp /path/to/cursor-engineering-rules/rules/*.mdc .cursor/rules/

# Or copy specific rules
cp /path/to/cursor-engineering-rules/rules/160-python.mdc .cursor/rules/
cp /path/to/cursor-engineering-rules/rules/280-aws.mdc .cursor/rules/
```

**Configure `.cursorrules`:**

```yaml
rules:
  - .cursor/rules/100-core.mdc
  - .cursor/rules/160-python.mdc
  - .cursor/rules/280-aws.mdc
```

---

### Method 3: Git Submodule (Recommended for Team Projects)

**Advantages:**
- Track specific version
- Easy updates via git
- Team consistency

**Setup:**

```bash
# From your project
cd /path/to/your/project

# Add as submodule
git submodule add https://github.com/d-padmanabhan/cursor-engineering-rules.git .cursor-rules

# Symlink to .cursor/rules
mkdir -p .cursor
ln -s ../.cursor-rules/rules .cursor/rules

# Team members clone with submodules
git clone --recurse-submodules <your-project-url>

# Or update existing clone
git submodule init
git submodule update
```

**Update rules:**

```bash
cd .cursor-rules
git pull origin main
cd ..
git add .cursor-rules
git commit -m "chore: update cursor rules"
```

---

## Configuration Strategies

### Strategy 1: Load All Rules (Comprehensive)

**Use when:**
- Large, complex projects
- Multiple technologies in one repo
- Want maximum guidance

**Configuration:**

```yaml
# .cursorrules
rulesDirectory: .cursor/rules
```

**Pros:**
- No maintenance needed
- All patterns available
- Consistent standards

**Cons:**
- May load unnecessary rules
- Slightly slower (negligible)

---

### Strategy 2: Selective Loading (Focused)

**Use when:**
- Clear technology stack
- Want faster rule loading
- Smaller projects

**Configuration:**

```yaml
# .cursorrules
rules:
  # Core (always include)
  - .cursor/rules/100-core.mdc
  - .cursor/rules/110-git.mdc
  - .cursor/rules/310-security.mdc
  
  # Your stack
  - .cursor/rules/160-python.mdc
  - .cursor/rules/280-aws.mdc
  - .cursor/rules/140-terraform.mdc
  
  # Optional
  - .cursor/rules/300-testing.mdc
  - .cursor/rules/220-documentation.mdc
```

**Pros:**
- Faster loading
- Clear dependencies
- Easy to understand

**Cons:**
- Manual maintenance
- May miss relevant rules

---

### Strategy 3: Progressive Enhancement (Start Small)

**Use when:**
- New to Cursor rules
- Evaluating value
- Small projects

**Phase 1: Core Only**

```yaml
rules:
  - .cursor/rules/100-core.mdc
  - .cursor/rules/110-git.mdc
```

**Phase 2: Add Language**

```yaml
rules:
  - .cursor/rules/100-core.mdc
  - .cursor/rules/110-git.mdc
  - .cursor/rules/160-python.mdc  # Your primary language
```

**Phase 3: Add Platform**

```yaml
rules:
  - .cursor/rules/100-core.mdc
  - .cursor/rules/110-git.mdc
  - .cursor/rules/160-python.mdc
  - .cursor/rules/280-aws.mdc     # Your cloud platform
```

**Phase 4: Add Patterns**

```yaml
rules:
  - .cursor/rules/100-core.mdc
  - .cursor/rules/110-git.mdc
  - .cursor/rules/160-python.mdc
  - .cursor/rules/280-aws.mdc
  - .cursor/rules/310-security.mdc
  - .cursor/rules/300-testing.mdc
```

---

## Rule Selection Guide

### By Project Type

#### Web Application (Full-Stack)
```yaml
rules:
  - .cursor/rules/100-core.mdc
  - .cursor/rules/110-git.mdc
  - .cursor/rules/165-typescript.mdc     # Frontend
  - .cursor/rules/160-python.mdc         # Backend
  - .cursor/rules/270-postgresql.mdc     # Database
  - .cursor/rules/320-api-design.mdc     # API patterns
  - .cursor/rules/310-security.mdc       # Security
  - .cursor/rules/300-testing.mdc        # Testing
```

#### Microservices (Go + Kubernetes)
```yaml
rules:
  - .cursor/rules/100-core.mdc
  - .cursor/rules/110-git.mdc
  - .cursor/rules/180-go.mdc
  - .cursor/rules/260-kubernetes.mdc
  - .cursor/rules/155-docker.mdc
  - .cursor/rules/330-observability.mdc
  - .cursor/rules/310-security.mdc
  - .cursor/rules/300-testing.mdc
```

#### Infrastructure/Platform Engineering
```yaml
rules:
  - .cursor/rules/100-core.mdc
  - .cursor/rules/110-git.mdc
  - .cursor/rules/130-bash.mdc
  - .cursor/rules/140-terraform.mdc
  - .cursor/rules/260-kubernetes.mdc
  - .cursor/rules/120-gha.mdc
  - .cursor/rules/310-security.mdc
```

#### Data Engineering
```yaml
rules:
  - .cursor/rules/100-core.mdc
  - .cursor/rules/110-git.mdc
  - .cursor/rules/160-python.mdc
  - .cursor/rules/270-postgresql.mdc
  - .cursor/rules/280-aws.mdc           # or 290-gcp.mdc
  - .cursor/rules/300-testing.mdc
```

#### AI/ML Application
```yaml
rules:
  - .cursor/rules/100-core.mdc
  - .cursor/rules/110-git.mdc
  - .cursor/rules/160-python.mdc
  - .cursor/rules/295-ai-ml.mdc
  - .cursor/rules/230-mcp-servers.mdc
  - .cursor/rules/280-aws.mdc           # Bedrock
  - .cursor/rules/310-security.mdc
```

---

## Testing Your Setup

### 1. Verify Rules Are Loaded

Open Cursor and check:
1. Go to Settings → Rules & Memories
2. Verify your rules appear in the list
3. Check that `alwaysApply` rules are marked

### 2. Test Code Generation

Ask Cursor to generate code that exercises your rules:

**Test Python rules:**
```
Generate a Python function to fetch data from an API with proper error handling, type hints, and async support.
```

**Test AWS rules:**
```
Create a Terraform module for an S3 bucket with versioning, encryption, and lifecycle policies.
```

**Test Security rules:**
```
Create a REST API endpoint with authentication, input validation, and rate limiting.
```

### 3. Verify Rule Application

Check that generated code follows patterns:
- ✅ Proper error handling
- ✅ Type annotations
- ✅ Security best practices
- ✅ Documentation
- ✅ Tests

---

## Troubleshooting

### Rules Not Loading

**Symptom:** Cursor ignores your rules

**Solutions:**

1. **Check file paths**
   ```bash
   ls -la .cursor/rules/
   cat .cursorrules
   ```

2. **Verify symlink** (if using symlinks)
   ```bash
   readlink .cursor/rules
   # Should show absolute path to rules directory
   ```

3. **Restart Cursor**
   - Quit completely (not just close window)
   - Reopen project

4. **Check Cursor settings**
   - Settings → Rules & Memories
   - Ensure rules are enabled

### Rules Conflict

**Symptom:** Unexpected code generation patterns

**Solutions:**

1. **Check rule order**
   - Later rules override earlier ones
   - Put more specific rules last

2. **Check `alwaysApply` rules**
   - These load automatically
   - May conflict with selective loading

3. **Use local overrides**
   - Create `999-local-overrides.mdc`
   - Override conflicting patterns

### Performance Issues

**Symptom:** Cursor is slow

**Solutions:**

1. **Reduce rules**
   - Use selective loading
   - Only load rules for your stack

2. **Optimize rule files**
   - Remove unused sections
   - Split large files

---

## Advanced Usage

### Custom Rule Development

Create project-specific rules:

```bash
# Create custom rule
vim .cursor/rules/999-local-overrides.mdc
```

```markdown
---
title: Project-Specific Overrides
description: Custom patterns for this project
priority: 999
alwaysApply: true
---

# Project Overrides

## Custom Pattern 1
[Your specific requirements]
```

### Environment-Specific Rules

Use different rules per environment:

```bash
# Development
cp .cursorrules.dev .cursorrules

# Production
cp .cursorrules.prod .cursorrules
```

### Team Standardization

For team projects:

1. **Commit `.cursorrules` to git**
   ```bash
   git add .cursorrules
   git commit -m "chore: add cursor rules configuration"
   ```

2. **Document in README**
   ```markdown
   ## Development Setup
   
   This project uses Cursor Engineering Rules:
   1. Clone with submodules: `git clone --recurse-submodules <url>`
   2. Rules are automatically loaded from `.cursor/rules`
   3. See `.cursorrules` for configuration
   ```

3. **Add to onboarding**
   - Include in team documentation
   - Mention in pull request templates
   - Reference in code review checklist

---

## 🎯 Quick Reference

### Essential Commands

```bash
# Setup (symlink method)
ln -s /path/to/cursor-engineering-rules/rules .cursor/rules

# Update rules (git submodule)
git submodule update --remote .cursor-rules

# Verify setup
ls -la .cursor/rules
cat .cursorrules

# Test
# (Ask Cursor to generate code)
```

### Key Files

- `.cursorrules` - Configuration file
- `.cursor/rules/` - Rules directory
- `999-local-overrides.mdc` - Project-specific rules

### Documentation

- [README.md](../README.md) - Overview
- [CONTRIBUTING.md](../CONTRIBUTING.md) - Contributing guidelines
- [rules/INDEX.md](../rules/INDEX.md) - Rule catalog

---

**Need Help?** Open an issue on [GitHub](https://github.com/d-padmanabhan/cursor-engineering-rules/issues)
