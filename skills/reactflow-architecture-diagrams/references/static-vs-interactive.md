# Static vs interactive architecture diagrams

| Aspect | Mermaid (Markdown) | React Flow (SPA) |
| --- | --- | --- |
| Where | `*.md`, ADRs, wiki | `*Diagram.tsx`, routed pages |
| Rule | `800-markdown.mdc` | `815-reactflow-diagrams.mdc` |
| Strength | Versioned text, easy review diff | Animation, logos, complex layout |
| Tradeoff | Less precision for icons | More code to maintain |

Pick one primary medium per deliverable; cross-link from docs to the SPA route when both exist.
