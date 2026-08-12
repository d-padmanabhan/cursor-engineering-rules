# Pydantic Validation Boundaries

Use Pydantic when structured untrusted data needs runtime validation, coercion policy, serialization, or schema generation. Prefer dataclasses or typed domain objects when data is already trusted and runtime validation adds no value.

## Boundary Decisions

Choose explicitly:

- whether unknown fields are rejected, ignored, or preserved;
- whether coercion is allowed or strict input types are required;
- normalization order and canonical representation;
- cross-field and model-level invariants;
- safe client errors versus diagnostic details;
- serialization aliases and fields that must never leave the process.

Pydantic defaults are not a universal security policy. At public or durable boundaries, rejecting unknown fields often catches misspellings and contract drift.

```python
from typing import Self

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class TransferRequest(BaseModel):
    """Validate a money-transfer request at the API boundary."""

    model_config = ConfigDict(extra="forbid", strict=True)

    source_account_id: str = Field(min_length=1, max_length=64)
    destination_account_id: str = Field(min_length=1, max_length=64)
    amount_cents: int = Field(gt=0)
    currency: str = Field(min_length=3, max_length=3)

    @field_validator("currency")
    @classmethod
    def normalize_currency(cls, value: str) -> str:
        """Normalize an ISO-style currency code."""
        return value.upper()

    @model_validator(mode="after")
    def reject_same_account(self) -> Self:
        """Reject transfers without distinct source and destination accounts."""
        if self.source_account_id == self.destination_account_id:
            raise ValueError("Source and destination accounts must differ")
        return self
```

## Parsing

- Use `Model.model_validate(mapping)` for Python objects.
- Use `Model.model_validate_json(payload)` for JSON bytes or strings.
- Validate once at the boundary, then pass typed domain values inward.
- Avoid repeatedly constructing models solely to revalidate already trusted values.
- Do not use `model_construct()` for untrusted input; it bypasses validation.

## Error Handling

Catch `ValidationError` at the boundary that owns the protocol response. Return stable, bounded field errors; do not expose stack traces, model internals, secrets, or unrestricted rejected values. Log aggregate failure context and correlation identifiers rather than entire payloads.

## Tests

Test:

- valid canonical input;
- missing and unknown fields;
- coercion accepted or rejected as designed;
- minimum, maximum, empty, and Unicode boundaries;
- cross-field invariants;
- safe serialization and excluded secrets;
- compatibility when schemas evolve.

Do not add validators that duplicate type or field constraints already expressed declaratively.
