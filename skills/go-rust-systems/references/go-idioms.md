# Go Idioms & Best Practices

## Go Proverbs (Core Principles)

These proverbs from Rob Pike guide idiomatic Go:

- **"Don't communicate by sharing memory, share memory by communicating"** - Use channels for coordination
- **"Concurrency is not parallelism"** - Concurrency is about structure, parallelism is about execution
- **"Channels orchestrate; mutexes serialize"** - Use channels for coordination, mutexes for mutual exclusion
- **"The bigger the interface, the weaker the abstraction"** - Keep interfaces small and focused
- **"Make the zero value useful"** - Types should work correctly when zero-initialized
- **"interface{} says nothing"** - Prefer specific types; use generics or type assertions when needed
- **"Gofmt's style is no one's favorite, yet gofmt is everyone's favorite"** - Always use `gofmt`
- **"A little copying is better than a little dependency"** - Prefer copying small code over adding dependencies
- **"Clear is better than clever"** - Readability over cleverness
- **"Reflection is never clear"** - Avoid reflection unless necessary
- **"Errors are values"** - Handle errors explicitly; don't ignore them
- **"Don't just check errors, handle them gracefully"** - Provide context and recovery paths
- **"Don't panic"** - Use errors, not panics, for normal error handling

## Make the Zero Value Useful

**Proverb**: "Make the zero value useful"

```go
//  GOOD: Zero value is useful
type Buffer struct {
    data []byte
}

func (b *Buffer) Write(p []byte) (int, error) {
    b.data = append(b.data, p...)
    return len(p), nil
}

// Can use without initialization:
var buf Buffer
buf.Write([]byte("hello"))  // Works!

//  GOOD: Zero value for sync primitives
var mu sync.Mutex
mu.Lock()  // Zero value mutex is ready to use

//  GOOD: Zero value for slices and maps
var users []User  // nil slice, safe to append
var cache map[string]int  // nil map, but must initialize before use

//  BAD: Zero value requires initialization to be safe
type Server struct {
    port int  // Zero value (0) is invalid!
}

func NewServer(port int) *Server {
    if port == 0 {
        panic("port required")  // Zero value not useful
    }
    return &Server{port: port}
}

//  GOOD: Zero value is safe
type Server struct {
    port int
}

func NewServer() *Server {
    return &Server{port: 8080}  // Sensible default
}

func (s *Server) SetPort(port int) {
    s.port = port
}
```

## Dependency Management

**Proverb**: "A little copying is better than a little dependency"

```go
//  BAD: Adding dependency for simple utility
import "github.com/some/lib/stringutils"

func process(s string) string {
    return stringutils.TrimAndLower(s)  // Dependency for 10 lines of code
}

//  GOOD: Copy small, stable utility code
func trimAndLower(s string) string {
    return strings.ToLower(strings.TrimSpace(s))
}

func process(s string) string {
    return trimAndLower(s)
}

//  GOOD: Use stdlib when possible
import (
    "strings"
    "fmt"
    "time"
)

//  BAD: External dependency for what stdlib provides
import "github.com/lib/timeutils"  // When time package works fine

//  GOOD: Add dependency only when:
//  - Functionality is complex (crypto, networking, parsing)
//  - Maintenance burden is high
//  - Code is large (>100 lines)
//  - It's a well-maintained, stable library
```

## Clear is Better Than Clever

**Proverb**: "Clear is better than clever"

```go
//  BAD: Clever but unclear
func process(data interface{}) interface{} {
    switch v := data.(type) {
    case int:
        return v * 2
    case string:
        return len(v)
    default:
        return nil
    }
}

//  GOOD: Clear and explicit
func DoubleInt(n int) int {
    return n * 2
}

func StringLength(s string) int {
    return len(s)
}

//  BAD: Clever one-liner
result := strings.Join([]string{strings.TrimSpace(s1), strings.TrimSpace(s2)}, ",")

//  GOOD: Clear and readable
s1Trimmed := strings.TrimSpace(s1)
s2Trimmed := strings.TrimSpace(s2)
result := strings.Join([]string{s1Trimmed, s2Trimmed}, ",")

//  BAD: Clever but confusing
func find(items []Item, fn func(Item) bool) *Item {
    for i := range items {
        if fn(items[i]) {
            return &items[i]
        }
    }
    return nil
}

//  GOOD: Clear intent
func FindItem(items []Item, predicate func(Item) bool) *Item {
    for i := range items {
        if predicate(items[i]) {
            return &items[i]
        }
    }
    return nil
}
```

## Avoid interface{} When Possible

**Proverb**: "interface{} says nothing"

```go
//  BAD: interface{} loses type safety
func Process(data interface{}) error {
    // Must use type assertions everywhere
    switch v := data.(type) {
    case string:
        // ...
    case int:
        // ...
    }
}

//  GOOD: Use generics (Go 1.18+)
func Process[T any](data T) error {
    // Type-safe, no assertions needed
    // ...
}

//  GOOD: Use specific types
func ProcessString(s string) error { /* ... */ }
func ProcessInt(n int) error { /* ... */ }

//  GOOD: Use type constraints for flexibility
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
```

## Project Layout

```
project/
 cmd/
    server/main.go
    cli/main.go
 internal/
    auth/
    handler/
 pkg/
    models/
 go.mod
 go.sum
```

## Naming

**Effective Go**: Names are important and have semantic effect (visibility).

- **`gofmt -s`**: Required ("Gofmt's style is no one's favorite, yet gofmt is everyone's favorite")
- **Imports**: Group as stdlib | third-party | internal
- **Exported**: PascalCase; unexported: camelCase
- **Doc comments (required for exported items)**: A `//` comment immediately preceding the declaration that **starts with the exported identifier name**, so `go doc` / `godoc` associates it correctly
- **Acronyms**: Uppercase (`HTTPServer`, `UserID`)
- **Interfaces**: `-er` suffix (`Reader`, `Hasher`) - keep interfaces small ("The bigger the interface, the weaker the abstraction")
- **Package names**: Lowercase, single-word, concise (`bytes`, `ring`, not `bytesPackage` or `ringPackage`)
- **Getters**: Don't use `Get` prefix (`Owner()`, not `GetOwner()`)

```go
//  GOOD: Package name is concise
package user  // Not userPackage or userManagement

// FetchIdentity retrieves the current AWS caller identity using STS.
// It returns an error if the request fails.
func FetchIdentity(ctx context.Context, client *sts.Client) (*sts.GetCallerIdentityOutput, error) {
    // ...
}

//  GOOD: Exported type uses package name context
type User struct {  // Users see it as user.User
    name string  // unexported field
}

//  GOOD: Getter without "Get" prefix (Effective Go)
func (u *User) Name() string {  // Not GetName()
    return u.name
}

//  GOOD: Setter can use "Set" prefix
func (u *User) SetName(name string) {
    u.name = name
}

//  GOOD: Small interface at consumer
type Reader interface {  // Small, focused
    Read([]byte) (int, error)
}

//  BAD: Large interface ("The bigger the interface, the weaker the abstraction")
type Everything interface {
    Read([]byte) (int, error)
    Write([]byte) (int, error)
    Close() error
    Flush() error
    Seek(int64, int) (int64, error)
    // ... too many methods
}
```

## Function Options Pattern

```go
type ServerOptions struct {
    Port int
    Host string
}

type ServerOption func(*ServerOptions)

func WithPort(port int) ServerOption {
    return func(o *ServerOptions) { o.Port = port }
}

func NewServer(opts ...ServerOption) *Server {
    cfg := ServerOptions{Port: 8080, Host: "localhost"}
    for _, opt := range opts {
        opt(&cfg)
    }
    return &Server{/* initialize */}
}
```
