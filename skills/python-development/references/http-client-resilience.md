# HTTP Client Resilience

Choose a client that already exists in the repository unless a required capability justifies another dependency. Reliability comes from ownership and policy, not from choosing `requests` or HTTPX by name.

## Client Ownership

- Reuse one client or session for related requests so connection pooling works.
- Give the client an explicit application, request, or task lifetime.
- Close clients with `with` or `async with`; do not rely on garbage collection.
- Do not create a client per request inside a hot loop.
- Configure TLS verification, proxy behavior, trust roots, and credentials centrally.
- Never log authorization headers, cookies, tokens, or unrestricted bodies.

```python
from collections.abc import Iterable, Iterator

import requests


def fetch_documents(urls: Iterable[str]) -> Iterator[dict[str, object]]:
    """Fetch documents with one bounded-lifetime connection pool."""
    with requests.Session() as session:
        for url in urls:
            response = session.get(url, timeout=(5, 30))
            response.raise_for_status()
            yield response.json()
```

## Timeout and Concurrency Budgets

- Every request needs a finite connect and response/read timeout.
- Bound the end-to-end operation separately; per-attempt timeouts do not cap all retries.
- Bound concurrent requests with a pool, semaphore, or queue.
- Size connection pools consistently with concurrency limits.
- Propagate cancellation rather than starting replacement work after the caller has stopped waiting.

## Retry Contract

Retry only when all are true:

1. The failure is classified as transient.
2. The operation is idempotent or uses a stable provider-supported idempotency key.
3. The retry fits within the caller's deadline and retry budget.
4. Backoff includes jitter and respects `Retry-After` where applicable.
5. Attempts and final exhaustion are observable.

Do not retry validation, authentication, authorization, most programming errors, or an ambiguous non-idempotent mutation. A timeout means the outcome may be unknown; reconcile authoritative state before repeating an unsafe mutation.

Avoid retry multiplication. Assign retries to one layer and account for load amplification across clients, gateways, SDKs, and workers.

## Response Handling

- Validate status before decoding a success body.
- Bound response size or stream large payloads.
- Validate media type and schema at the trust boundary.
- Decide whether partial streaming output is retryable before exposing it to callers.
- Treat redirects and caller-supplied URLs as SSRF-sensitive behavior.
- Separate safe client-facing errors from diagnostic logs.

## Async Clients

The same ownership rules apply to async clients. Keep one `aiohttp.ClientSession` or `httpx.AsyncClient` for the operation/application lifetime, use an async context manager, set deadlines, and bound tasks. Follow the [async and concurrency reference](file:///Users/Devesh_Padmanabhan/.cursor/agent-engineering-handbook/skills/python-development/references/async-concurrency.md) for `TaskGroup`, cancellation, and concurrency limits.
