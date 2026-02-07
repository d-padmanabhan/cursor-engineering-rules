# Go Generics (Go 1.18+)

## Generic Functions

```go
// GOOD: Generic function for any comparable type
func Find[T comparable](slice []T, value T) (int, bool) {
    for i, v := range slice {
        if v == value {
            return i, true
        }
    }
    return -1, false
}

// Usage
idx, found := Find([]string{"a", "b", "c"}, "b")
idx, found := Find([]int{1, 2, 3}, 2)
```

## Generic Types

```go
// Generic stack
type Stack[T any] struct {
    items []T
    mu    sync.Mutex
}

func NewStack[T any]() *Stack[T] {
    return &Stack[T]{items: make([]T, 0)}
}

func (s *Stack[T]) Push(item T) {
    s.mu.Lock()
    defer s.mu.Unlock()
    s.items = append(s.items, item)
}

func (s *Stack[T]) Pop() (T, bool) {
    s.mu.Lock()
    defer s.mu.Unlock()

    if len(s.items) == 0 {
        var zero T
        return zero, false
    }

    item := s.items[len(s.items)-1]
    s.items = s.items[:len(s.items)-1]
    return item, true
}

// Usage
stringStack := NewStack[string]()
stringStack.Push("hello")
stringStack.Push("world")

intStack := NewStack[int]()
intStack.Push(1)
intStack.Push(2)
```

## Type Constraints

```go
// Numeric constraint
type Numeric interface {
    ~int | ~int64 | ~float64
}

func Sum[T Numeric](items []T) T {
    var sum T
    for _, item := range items {
        sum += item
    }
    return sum
}

// Comparable constraint
func Max[T comparable](a, b T) T {
    // Note: comparable doesn't support < or >
    // Use constraints.Ordered for comparisons
}

import "golang.org/x/exp/constraints"

func Max[T constraints.Ordered](a, b T) T {
    if a > b {
        return a
    }
    return b
}
```

## Generic Interfaces

```go
// Generic repository pattern
type Repository[T any, ID comparable] interface {
    Get(ctx context.Context, id ID) (*T, error)
    Create(ctx context.Context, entity *T) error
    Update(ctx context.Context, id ID, entity *T) error
    Delete(ctx context.Context, id ID) error
}

type UserRepository struct {
    db *sql.DB
}

func (r *UserRepository) Get(ctx context.Context, id string) (*User, error) {
    // Implementation
}

func (r *UserRepository) Create(ctx context.Context, user *User) error {
    // Implementation
}
```
