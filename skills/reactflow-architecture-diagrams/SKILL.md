---
name: reactflow-architecture-diagrams
description: >-
  Delivers narrative interactive architecture diagrams using React, TypeScript,
  Tailwind, and @xyflow/react (React Flow): node and edge patterns, optional
  Cloudflare orange shell grouping, routing, and verification. Use when adding
  or editing React Flow diagram components (Diagram.tsx suffix convention),
  files under components/diagrams, xyflow
  edges, animated canvas traffic, or when the user asks for a React Flow
  architecture diagram alongside documentation.
---

# React Flow architecture diagrams

## Canonical rule

Follow **`rules/815-reactflow-diagrams.mdc`** for do/don't lists, file globs, and edge semantics. This skill is the **playbook**; the rule is the **contract**.

## When to use Mermaid vs React Flow

- **Mermaid** (see `rules/800-markdown.mdc` and `skills/documentation-standards`): static diagrams in Markdown, ADRs, GitHub-rendered docs.
- **React Flow**: interactive or animated canvases, custom nodes (logos, multi-line cards), and **legend + diagram** product pages.

## Playbook: add a new diagram to an existing SPA

1. **Pick a reference** diagram in the same app (or copy patterns from `815`) and reduce scope; keep one story per canvas.
2. **Implement** `buildNodesAndEdges()` (or equivalent) returning `{ nodes, edges }`. Keep `nodeTypes` and `edgeTypes` at **module scope** with `memo()`-wrapped components.
3. **Add** a route page: title, scope (what one request or one flow shows), optional static reference image, **How to read** bullets that map **colors and line styles** to meaning, then `<YourDiagram />`.
4. **Wire** the router and home or index links; update **README** routes and assets tables when paths or figures change.
5. **Run** lint and production build from the app directory.

## Playbook: Cloudflare-scoped traffic

1. Add a **parent** shell node (`cfShell` or your name) with fixed width/height and `overflow: 'visible'`.
2. Nest **child** nodes with `parentId` + `extent: 'parent'`; convert world coordinates to **parent-relative** positions.
3. Use **opaque inner cards** for text-heavy nodes sitting on the orange frame (see `815`).

## Playbook: identity and edge cases

- **JWKS / metadata fetch** is not the same as **OIDC login**. If both appear, use **dashed** edges and distinct colors for issuance vs verification, and say so in page copy.

## Verification

Do not skip **lint** and **build** (or `tsc -b`) after graph or handle changes; broken `Handle` ids fail at runtime.
