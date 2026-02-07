# LLM and RAG patterns (non-MCP specific)

This reference captures high-signal patterns for LLM application design beyond MCP mechanics: prompt structure, retrieval, and safety boundaries.

---

## Prompting and instruction hygiene

- Keep a single “goal” statement and explicit non-goals
- Put constraints in one place and keep them testable
- Prefer structured output formats (tables, checklists) when humans need to review
- Avoid hidden “magic” behaviors that are hard to verify

---

## RAG (retrieval-augmented generation)

### Minimal RAG pipeline

1. Ingest documents
2. Chunk content (preserve headings)
3. Embed chunks
4. Retrieve top-k by similarity
5. Re-rank (optional)
6. Answer with citations (doc + section)

### Chunking guidance

- Chunk by headings first, then by size
- Preserve source metadata (URL/file path, heading hierarchy)
- Avoid mixing unrelated topics in one chunk

### Retrieval guidance

- Use a small `top_k` first, then expand if recall is insufficient
- Prefer filtering by doc type/source before broad similarity search
- Cache retrieval results for repeated queries where safe

---

## Safety and data handling

- Do not send secrets to the model (API keys, tokens, private keys)
- Redact sensitive values in logs and prompts
- Separate “user input” from “system constraints” in the prompt structure
- Require explicit confirmation before destructive actions (deletes, pushes, applies)
