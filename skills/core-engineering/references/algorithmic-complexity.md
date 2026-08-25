# Algorithmic Complexity

Use asymptotic analysis to explain how resource use grows with input. Use benchmarks and production measurements to determine whether that growth matters in the real workload.

## Analysis Procedure

1. Define input variables and bounds.
2. Identify the dominant operations.
3. Count sequential, nested, recursive, and repeated work.
4. Analyze worst-case time and auxiliary space.
5. Add average, expected, amortized, output-sensitive, or external-I/O qualifications when relevant.
6. State assumptions about data structures, ordering, hashing, and input distribution.
7. Compare the current and proposed designs.
8. Define a measurement that can confirm the expected impact.

Example:

```text
n = number of orders
m = number of blocked customer IDs

Current:
- scan m blocked IDs for each order
- time: O(n * m)
- auxiliary space: O(1)

Proposed:
- construct a hash set from m IDs, then test each order
- expected time: O(n + m)
- auxiliary space: O(m)
- worst-case lookup depends on hash-table implementation and collision behavior
```

## Combining Work

### Sequential phases

```text
scan n records, then scan m rules: O(n + m)
```

Do not simplify to `O(max(n, m))` when naming both independent inputs communicates the design more clearly.

### Nested phases

```text
compare every one of n records with every one of m rules: O(n * m)
```

Two loops are not automatically quadratic. Consecutive loops are additive; nested loops depend on their bounds.

### Halving or doubling

Repeatedly halving the remaining search space is `O(log n)`. Processing all `n` items at each of `log n` levels is commonly `O(n log n)`.

### Output-sensitive work

If an operation must emit `k` results, its runtime cannot be less than `O(k)` merely because lookup is efficient. State complexity using all meaningful variables, such as `O(n + k)`.

## Time and Space Cases

State which case is being analyzed:

- **Worst case**: default for correctness and capacity reasoning.
- **Average case**: valid only with a stated input distribution.
- **Expected case**: often depends on randomized behavior or hashing assumptions.
- **Amortized case**: cost averaged over a sequence of operations, such as dynamic-array growth.
- **Best case**: rarely useful alone for production decisions.

Amortized `O(1)` append does not mean every append is constant-time. A resize operation can copy the existing collection.

Auxiliary space excludes the input and required output unless the decision specifically concerns total resident memory. State which definition is used.

## Common Operation Caveats

| Operation | Typical model | Caveat |
|---|---|---|
| Array indexing | `O(1)` | Bounds checks and cache behavior affect constants |
| Linear search | `O(n)` | Can stop early, but worst case examines all items |
| Binary search | `O(log n)` | Requires suitable ordered random-access data |
| Comparison sort | `O(n log n)` | Some algorithms have different worst-case or memory behavior |
| Hash lookup | Expected `O(1)` | Worst case and adversarial collision behavior differ |
| Balanced tree lookup | `O(log n)` | Depends on balancing guarantees |
| Heap insert/remove | `O(log n)` | Reading the extremum is commonly `O(1)` |
| Graph traversal | `O(V + E)` | Representation changes memory and constants |
| String concatenation in a loop | Can become `O(n^2)` | Depends on immutability, copying, and total output size |

Verify the actual language and library contract before asserting a data structure's guarantee.

## External Operations

Big O does not replace system-level cost analysis:

- An `O(n)` loop issuing `n` network calls is dominated by round trips and dependency capacity.
- An ORM property access inside a loop can create an N+1 query pattern.
- Pagination may be linear in returned items but unsafe if page count, memory, or cursor progress is unbounded.
- Database complexity depends on indexes, cardinality, plan choice, data distribution, and returned rows.
- Parallelism may reduce elapsed time while increasing total work, contention, memory, or downstream load.

Count calls, bytes, allocations, queueing, and concurrency in addition to asymptotic CPU work.

## Review Format

For a material complexity finding, report:

1. **Input model**: variables, expected sizes, and bounds.
2. **Current complexity**: time, space, and dominant operation.
3. **Failure threshold**: where latency, memory, or call volume becomes unacceptable.
4. **Smallest correction**: behavior-preserving implementation or design.
5. **New complexity**: including added memory or preprocessing.
6. **Measurement**: representative benchmark, profile, query plan, or production metric.

Avoid:

- declaring all nested loops `O(n^2)`;
- dropping independent variables;
- treating expected hash lookup as a guaranteed worst-case bound;
- ignoring the cost to build an index or set;
- optimizing a tiny fixed collection without evidence;
- reporting notation without a concrete implementation consequence.
