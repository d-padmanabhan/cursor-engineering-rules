# Teradata notes

## Performance stability

- PI (distribution) and stats often dominate performance outcomes.
- Spool blowups usually come from many-to-many joins and large intermediate sorts.

## Safety

- Use `EXPLAIN` for new large query shapes.
- Apply `475-sql.mdc` destructive-operation guardrails for DML/DDL.
