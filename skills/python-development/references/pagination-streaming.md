# Pagination and Streaming

Treat pagination as a protocol with termination, ordering, retry, and resource limits, not as a loop that appends until a field is empty.

## Contract

- Treat cursors and continuation tokens as opaque.
- Preserve the provider's required request parameters across pages.
- Stop when the provider explicitly signals completion.
- Detect repeated cursors and pages that make no progress.
- Set page and total-item limits when input or provider behavior is untrusted.
- Define whether partial results may be returned after a later-page failure.
- Preserve stable ordering only when the provider contract guarantees it.
- Stream pages or items by default; accumulate only when the caller requires a bounded collection.
- Propagate timeout, cancellation, and rate-limit behavior through every page request.
- Do not retry a whole pagination run blindly after emitting partial results.

## Bounded Iterator

```python
from collections.abc import Callable, Iterator
from dataclasses import dataclass


@dataclass(frozen=True)
class Page[T]:
    """Represent one page returned by a provider."""

    items: tuple[T, ...]
    next_cursor: str | None


def iter_items[T](
    fetch_page: Callable[[str | None, int], Page[T]],
    *,
    page_size: int = 100,
    max_pages: int = 10_000,
) -> Iterator[T]:
    """Yield items while enforcing pagination progress and limits."""
    cursor: str | None = None
    seen_cursors: set[str] = set()

    for _ in range(max_pages):
        page = fetch_page(cursor, page_size)
        yield from page.items

        if page.next_cursor is None:
            return
        if page.next_cursor == cursor or page.next_cursor in seen_cursors:
            raise RuntimeError("Pagination cursor did not make progress")

        seen_cursors.add(page.next_cursor)
        cursor = page.next_cursor

    raise RuntimeError(f"Pagination exceeded {max_pages} pages")
```

For offset pagination over mutable data, inserts and deletes can cause duplicates or omissions. Prefer a provider-supported stable cursor or keyset based on a deterministic unique ordering.

## Recovery and Observability

Record page count, item count, latency, retries, rate-limit waits, and terminal cursor state without logging sensitive cursor contents. If resumability is required, checkpoint only after downstream effects are durable and idempotent.

AWS APIs should use service paginators rather than hand-built token loops; see the AWS and Boto3 reference (`${HANDBOOK_ROOT}/skills/python-development/references/aws-boto3.md`).
