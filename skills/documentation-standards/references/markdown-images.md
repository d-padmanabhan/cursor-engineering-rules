# Markdown and Generated Images

Use generated PNG diagrams for static visuals in Markdown and MDX. Do not
author Mermaid blocks.

## Decide Whether an Image Is Needed

Use an image when it materially clarifies:

- architecture or data flow;
- an interaction sequence;
- state transitions;
- hierarchy or ownership;
- a timeline or comparison that prose cannot express concisely.

Prefer prose or a short list for simple relationships. Do not generate
decorative images or create an empty image directory.

## Placement and Naming

Create an `images/` directory beside the Markdown file that owns the image:

```text
docs/
├── architecture.md
└── images/
    └── request-processing-flow.png
```

Use lowercase kebab-case filenames that describe the diagram. Avoid names such
as `image.png`, `diagram-1.png`, timestamps, or random identifiers.

Do not place a document-specific image in a distant shared asset directory.
When multiple documents intentionally share one image, document that ownership
and choose one stable shared location.

## Markdown Embedding

Reference the PNG through a portable path relative to the Markdown file:

```markdown
![A request moves from the client through the API to storage](images/request-processing-flow.png)
```

Do not use absolute filesystem paths, `file://` URLs, or user-specific home
directories. Keep filename case identical to the file on disk.

Alt text must communicate the purpose or key relationship. Do not repeat the
filename or use generic text such as "diagram" or "image." Put detailed
explanation in surrounding prose when the full visual cannot be conveyed
concisely.

## Generation Contract

Before generating, define:

- the question the image must answer;
- required components and relationships;
- labels and terminology;
- trust or ownership boundaries when relevant;
- orientation and expected rendered size;
- information that must be excluded.

Generate a PNG at sufficient resolution for readable labels without requiring
browser zoom. Prefer a simple layout, high contrast, and a limited visual
vocabulary. Do not encode meaning through color alone.

Inspect the resulting artifact. Regenerate it when labels are clipped,
relationships are wrong, arrows are ambiguous, text is unreadable, or the
image introduces unsupported details.

## Security and Privacy

Treat image content and generation prompts as data egress.

- Never include passwords, tokens, keys, connection strings, credentials, or
  production secrets.
- Replace real customer, employee, account, tenant, host, and resource
  identifiers with approved synthetic values.
- Exclude raw production screenshots unless collection, redaction, retention,
  and publication are explicitly authorized.
- Do not send confidential architecture or data to an unapproved image
  provider.
- Inspect generated metadata and visible text before publication.

## Version Control and Lifecycle

The PNG is part of the documentation change. Include it with the Markdown file
when repository policy permits generated binary documentation artifacts.

When updating the surrounding design:

- confirm that the image still matches the text and implementation;
- regenerate stale images rather than editing prose around an incorrect visual;
- remove unreferenced images owned only by that document when removal is in
  scope;
- review binary size and avoid unnecessarily large artifacts.

## Verification

Before completion:

1. confirm the PNG exists at the referenced relative path;
2. render the Markdown in the target documentation system;
3. check image dimensions, legibility, clipping, and contrast;
4. verify alt text and surrounding explanation;
5. verify the image contains no sensitive or misleading content;
6. run Markdown lint and link or asset checks;
7. inspect the final diff for orphaned or unexpectedly large files.
