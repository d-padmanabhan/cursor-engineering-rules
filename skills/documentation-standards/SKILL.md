---
name: documentation-standards
description: >-
  Documentation best practices including Markdown formatting, generated PNG
  diagrams, technical writing, ADRs, Docusaurus and MDX documentation sites,
  and open source standards. Use when writing documentation, README files,
  Markdown or MDX content, creating static diagrams for Markdown, configuring
  Docusaurus, or asking about documentation structure, technical writing, or
  open source project setup. For interactive React Flow canvases in a SPA, use
  the reactflow-architecture-diagrams skill instead.
---

# Documentation Standards

Mandatory Markdown gates are owned by the Markdown rule (`${HANDBOOK_ROOT}/rules/800-markdown.mdc`). This skill owns document design, generated PNG guidance, templates, and writing workflows.

## Core Principles

1. **Audience-First**: Write for your reader, not yourself
2. **Keep Current**: Outdated docs are worse than no docs
3. **Show, Don't Just Tell**: Use examples and diagrams
4. **Consistent Format**: Follow established patterns

## Hard Requirements (Writing)

- **No AI slop** - remove filler, keep docs concrete and task-oriented
- **No Unicode em dashes or en dashes** - never author `U+2014` or `U+2013`; use commas, colons, parentheses, semicolons, or ASCII hyphens instead
- **Clickable navigation** - if readers may want to open a repo file, directory, section, ADR, rule, skill, script, workflow, or config, make it a Markdown link. Use backticks only when the path is a literal value, not a navigation target.
- **Official terminology** - use each vendor's current official product and service names, capitalization, and branding. Verify uncertain names against current vendor documentation. For example, write **Amazon VPC**, not **AWS VPC**; write **AWS Lambda**, not **Amazon Lambda**. Do not apply one naming prefix mechanically across a provider's services.

## Voice

Prefer neutral/imperative phrasing - avoid "you/your" in professional docs.
Canonical guidance: `rules/810-documentation.mdc`.

## Diataxis Quick Guide

Use one primary documentation mode per page:

- **Tutorial** - learning by doing
- **How-to guide** - task completion
- **Reference** - factual lookup
- **Explanation** - concepts and rationale

Canonical Diataxis guidance lives in `rules/810-documentation.mdc`. Keep this skill concise and link back to the rule instead of duplicating detailed standards.

## Documentation Sites and Docusaurus

Use a documentation site when the content needs structured multi-page
navigation, search, versioning, internationalization, or interactive MDX.
Keep a README and a small set of Markdown guides when those capabilities do not
justify a separate Node.js build and deployment lifecycle.

For Docusaurus work:

- Verify the current supported Docusaurus, Node.js, React, and plugin versions
  from official sources. Pin compatible releases and commit the lockfile.
- Treat MDX as executable React code. Never compile untrusted content as MDX.
- Configure search explicitly. Docusaurus does not make a site searchable
  without a search integration and index lifecycle.
- Version only supported release lines, not every patch by default.
- Make the production build fail on broken internal links and verify `url`,
  `baseUrl`, and `trailingSlash` against the deployment path.

Use the Docusaurus reference
(`${HANDBOOK_ROOT}/skills/documentation-standards/references/docusaurus.md`) for
site structure, MDX trust boundaries, versioning, search, CI, and deployment.

## README Structure

```markdown
# Project Name

Brief description of what this project does.

## Features

- Feature 1
- Feature 2

## Installation

```bash
npm install my-project
```

## Quick Start

```javascript
import { thing } from 'my-project';
thing.doSomething();
```

## Documentation

Link to full docs.

## Contributing

Link to CONTRIBUTING.md.

## License

MIT - See LICENSE.

```

## Markdown Best Practices

### Headers
- Use `#` hierarchy (don't skip levels)
- Keep headers concise
- Use title case for headings, preserving established acronyms and product names

### Code Blocks
````markdown
```python
def hello():
    print("Hello, World!")
```

````

### Lists
```markdown
- Unordered item
- Another item
  - Nested item

1. Ordered item
2. Another item
```

### Links and References
```markdown
[Link text](https://acme.com)
[Reference link][1]
Python rule (`${HANDBOOK_ROOT}/rules/200-python.mdc`)
Bash rule (`${HANDBOOK_ROOT}/rules/140-bash.mdc`)

[1]: https://acme.com
```

Prefer clickable same-repo references:

- Good: `Python skill (`${HANDBOOK_ROOT}/skills/python-development/SKILL.md`)`
- Avoid for navigation: `` `skills/python-development/` ``
- Good for literals: `` `src/app.ts` `` when discussing a path value or config example

### Tables
```markdown
| Header 1 | Header 2 |
|----------|----------|
| Cell 1   | Cell 2   |
```

## Static and Interactive Diagrams

- **Static Markdown documentation:** generate a PNG under an `images/`
  directory beside the Markdown file and embed it with a relative path.
- **Interactive React application:** use the React Flow rule
  (`${HANDBOOK_ROOT}/rules/815-reactflow-diagrams.mdc`) and skill
  (`${HANDBOOK_ROOT}/skills/reactflow-architecture-diagrams/SKILL.md`).

Do not author Mermaid blocks in Markdown or MDX.

## Generated PNG Workflow

1. Decide whether the relationship is materially clearer as an image than as
   short prose or a list.
2. Create an `images/` directory in the directory containing the Markdown file.
3. Generate a focused PNG with a descriptive kebab-case filename.
4. Inspect the image for correctness, legibility, clipping, misleading arrows,
   accidental sensitive data, and unnecessary decoration.
5. Embed it with meaningful alt text and a portable relative path.
6. Verify the image from the rendered document.

For `docs/design.md`, the required layout is:

```text
docs/
├── design.md
└── images/
    └── request-flow.png
```

Embed the generated artifact with meaningful alt text and the portable relative
path `images/request-flow.png`. Use the detailed Markdown images reference for
the exact syntax.

Do not create an empty `images/` directory when no diagram is needed. Do not
place generated images in a repository-wide asset directory when the image is
owned by one nearby document.

## Technical Writing Tips

1. **Use active voice**: "The function returns a value" not "A value is returned"
2. **Be concise**: Remove unnecessary words
3. **Define acronyms**: Spell out on first use
4. **Use present tense**: "The function adds" not "The function will add"
5. **Include examples**: Show, don't just tell

## Detailed References

- **React Flow (interactive canvases)**: See `skills/reactflow-architecture-diagrams/SKILL.md` and `rules/815-reactflow-diagrams.mdc`
- **Docusaurus**: See Docusaurus documentation sites (`${HANDBOOK_ROOT}/skills/documentation-standards/references/docusaurus.md`)
- **Markdown and images**: See Markdown images (`${HANDBOOK_ROOT}/skills/documentation-standards/references/markdown-images.md`)
- **Technical Writing**: See technical writing (`${HANDBOOK_ROOT}/skills/documentation-standards/references/technical-writing.md`)
- **Open Source**: See open source (`${HANDBOOK_ROOT}/skills/documentation-standards/references/open-source.md`)
