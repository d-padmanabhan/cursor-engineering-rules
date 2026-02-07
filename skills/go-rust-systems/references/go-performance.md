# Go Performance Optimization

**Golden Rule:** Measure first, optimize second. Use benchmarks and profiling to guide optimization.

## Measurement Required

```go
func BenchmarkProcessData(b *testing.B) {
    data := generateTestData()
    b.ResetTimer()
    b.ReportAllocs()

    for i := 0; i < b.N; i++ {
        ProcessData(data)
    }
}
```

## Performance Optimization Examples

**Slice Pre-allocation:**

```go
// BAD: Grows slice dynamically
var result []int
for i := 0; i < 1000; i++ {
    result = append(result, i*2)  // May cause multiple allocations
}

// GOOD: Pre-allocate with known capacity
result := make([]int, 0, 1000)
for i := 0; i < 1000; i++ {
    result = append(result, i*2)  // No reallocation
}

// GOOD: Pre-allocate with known length
result := make([]int, 1000)
for i := 0; i < 1000; i++ {
    result[i] = i * 2
}
```

**String Building:**

```go
// BAD: String concatenation (creates new strings)
var result string
for _, part := range parts {
    result += part  // O(n²) complexity
}

// GOOD: strings.Builder
var sb strings.Builder
sb.Grow(estimatedSize)  // Pre-allocate if size known
for _, part := range parts {
    sb.WriteString(part)
}
result := sb.String()

// GOOD: For small, known strings, use fmt.Sprintf
result := fmt.Sprintf("%s-%s-%s", part1, part2, part3)
```

**Map Pre-allocation:**

```go
// BAD: Map grows dynamically
cache := make(map[string]int)
for _, key := range keys {
    cache[key] = process(key)
}

// GOOD: Pre-allocate if size known
cache := make(map[string]int, len(keys))
for _, key := range keys {
    cache[key] = process(key)
}
```

**Avoid Unnecessary Allocations:**

```go
// BAD: Unnecessary allocation in hot path
func process(items []Item) {
    for _, item := range items {
        data := make(map[string]interface{})  // Allocated each iteration
        data["key"] = item.Value
        processData(data)
    }
}

// GOOD: Reuse allocation
func process(items []Item) {
    data := make(map[string]interface{})  // Allocated once
    for _, item := range items {
        data["key"] = item.Value
        processData(data)
        // Clear for next iteration if needed
        for k := range data {
            delete(data, k)
        }
    }
}
```

**Efficient Lookups:**

```go
// BAD: Linear search
func findUser(users []User, id string) *User {
    for _, user := range users {
        if user.ID == id {
            return &user
        }
    }
    return nil
}

// GOOD: Use map for O(1) lookup
type UserIndex map[string]*User

func buildIndex(users []User) UserIndex {
    index := make(UserIndex, len(users))
    for i := range users {
        index[users[i].ID] = &users[i]
    }
    return index
}
```

**Memory Management:**

```go
// GOOD: Preallocate slice
users := make([]User, 0, expectedCount)

// GOOD: strings.Builder for concatenation
var sb strings.Builder
sb.Grow(estimatedSize)
for _, part := range parts {
    sb.WriteString(part)
}
result := sb.String()

// GOOD: Use sync.Pool for frequently allocated objects
var bufferPool = sync.Pool{
    New: func() interface{} {
        return new(bytes.Buffer)
    },
}

func getBuffer() *bytes.Buffer {
    return bufferPool.Get().(*bytes.Buffer)
}

func putBuffer(buf *bytes.Buffer) {
    buf.Reset()
    bufferPool.Put(buf)
}
```

**CPU Optimization:**

```go
// BAD: Inefficient algorithm
func findDuplicates(items []int) []int {
    var duplicates []int
    for i, item1 := range items {
        for j, item2 := range items {
            if i != j && item1 == item2 {
                duplicates = append(duplicates, item1)
                break
            }
        }
    }
    return duplicates  // O(n²)
}

// GOOD: Efficient algorithm with map
func findDuplicates(items []int) []int {
    seen := make(map[int]bool, len(items))
    duplicates := make([]int, 0)

    for _, item := range items {
        if seen[item] {
            duplicates = append(duplicates, item)
        } else {
            seen[item] = true
        }
    }
    return duplicates  // O(n)
}
```

**Avoid Interface Conversions:**

```go
// BAD: Interface conversion in hot path
func process(items []interface{}) {
    for _, item := range items {
        switch v := item.(type) {
        case int:
            processInt(v)
        case string:
            processString(v)
        }
    }
}

// GOOD: Use generics or specific types
func processInts(items []int) {
    for _, item := range items {
        processInt(item)
    }
}
```
