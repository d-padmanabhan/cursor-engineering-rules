# Rust Documentation and Public API Contracts

Rust documentation is part of the public API. It must explain behavior the type signature cannot express and remain executable where practical.

## Documentation Surface

- Put crate front-page documentation at the top of `lib.rs` with `//!`. Explain purpose, primary entry points, important features, and material constraints.
- Use `//!` for module documentation and `///` for public items.
- Give each public item a concise summary before details.
- Use intra-doc links such as [`Client`] and [`Client::close`] so rustdoc verifies destinations. Add a disambiguator such as `struct@` or `fn@` only when names are ambiguous.
- Review reexports from the caller's view. Use `#[doc(inline)]` or `#[doc(no_inline)]` deliberately when the generated API surface would otherwise be confusing.
- Explain feature flags that change availability, behavior, safety, or dependencies.
- Do not repeat parameter and return types already shown in the signature. Document semantic constraints, units, ownership, mutation, ordering, blocking, cancellation, side effects, thread safety, and resource lifecycle.
- Do not document obvious private helpers merely to increase coverage.

The official [rustdoc writing guide](https://doc.rust-lang.org/rustdoc/how-to-write-documentation.html) recommends documenting public APIs while avoiding prose that duplicates signature types.

## Useful Sections

Add sections only when the contract requires them:

- `# Examples` for the smallest copyable happy path.
- `# Errors` for conditions represented by `Result`.
- `# Panics` for reachable panic conditions callers must prevent or accept.
- `# Safety` for the obligations of every public `unsafe` function, trait, method, or implementation.

```rust
//! Bounded clients for the ACME document service.

use std::time::Duration;

/// Reads one document before the supplied deadline.
///
/// The returned future borrows `client` and may be cancelled by dropping it.
/// The client remains reusable after cancellation.
///
/// # Examples
///
/// ```no_run
/// # use acme_client::{Client, ClientError};
/// # use std::time::Duration;
/// # async fn example() -> Result<(), ClientError> {
/// let client = Client::connect().await?;
/// let document = client.read("doc-42", Duration::from_secs(2)).await?;
/// assert_eq!(document.id(), "doc-42");
/// client.close().await?;
/// # Ok(())
/// # }
/// ```
///
/// # Errors
///
/// Returns [`ClientError::DeadlineExceeded`] when the operation does not
/// complete before `timeout`.
pub async fn read(
    client: &Client,
    document_id: &str,
    timeout: Duration,
) -> Result<Document, ClientError> {
    client.read_with_timeout(document_id, timeout).await
}
```

## Doctests

Rustdoc executes Rust code blocks as documentation tests. Use them as part of the compatibility contract.

- Prefer ordinary Rust code blocks when the example can run without external systems.
- Prefix setup lines with `#` to compile them while hiding noise from rendered documentation.
- Use `no_run` when code must compile but cannot safely execute in a doctest, such as network calls or process termination.
- Use `compile_fail` only when compilation failure is the behavior being taught. Keep such tests narrow because future compiler changes can make previously invalid code compile.
- Use `ignore` only for a documented platform or toolchain limitation. It disables compilation and should not hide incomplete examples.
- Mark pseudocode as `text`, not ignored Rust.
- Keep examples deterministic, bounded, and free of real credentials or network dependencies.

See the official [documentation tests guide](https://doc.rust-lang.org/rustdoc/write-documentation/documentation-tests.html) for code block attributes and hidden setup.

## Unsafe Contracts

Every public unsafe API needs a `# Safety` section describing all obligations a caller must uphold. Every unsafe block needs a nearby `// SAFETY:` comment describing why those obligations hold at that exact call site.

```rust
/// Reads a value from a non-null, properly aligned pointer.
///
/// # Safety
///
/// `pointer` must be valid and aligned for reading one initialized `u32`.
/// The referenced allocation must remain alive for the duration of this call.
pub unsafe fn read_u32(pointer: *const u32) -> u32 {
    // SAFETY: The caller contract guarantees validity, alignment, initialization,
    // and allocation lifetime for one u32 read.
    unsafe { pointer.read() }
}
```

A vague comment such as `// SAFETY: safe because checked` is insufficient. State the concrete invariant, validation, provenance, bounds, aliasing rule, initialization state, and lifetime that justify the operation.

## Lints and CI

Adopt lint severity according to repository maturity. New public libraries should normally deny missing documentation. Existing crates may start at `warn` and tighten after closing the backlog.

```rust
#![warn(missing_docs)]
#![warn(rustdoc::missing_crate_level_docs)]
#![deny(rustdoc::broken_intra_doc_links)]
#![warn(clippy::missing_safety_doc)]
#![warn(clippy::undocumented_unsafe_blocks)]
```

`clippy::missing_safety_doc` is a style lint. `clippy::undocumented_unsafe_blocks` is restriction-allow by default, so enable it explicitly when the repository requires local safety justifications. The [Clippy lint catalog](https://rust-lang.github.io/rust-clippy/master/index.html) is the current source for lint names, groups, and default levels.

Run:

```bash
cargo test --doc
RUSTDOCFLAGS="-D warnings" cargo doc --no-deps
cargo clippy --all-targets --all-features -- -D warnings
```

Run relevant feature combinations when APIs are conditional. `--all-features` is not proof that every mutually exclusive or no-default-features combination works.

## Suppression Discipline

- Fix the documentation or unsafe invariant before suppressing a diagnostic.
- Scope an unavoidable `#[allow(...)]` to the smallest item.
- Add a rationale, owner, and removal condition for policy exceptions.
- Never use `#[allow(missing_docs)]`, `#[allow(clippy::missing_safety_doc)]`, ignored doctests, or broad lint-group allowances to make CI green without resolving the contract defect.
- Review generated code separately. Generated output may have a documented exception when the generator is the maintained source of truth.

The official [rustdoc lint catalog](https://doc.rust-lang.org/rustdoc/lints.html) documents rustdoc-only lints and their default levels.
