# Go Patterns

## Context & Cancellation

```go
// Context as first parameter
func fetchUser(ctx context.Context, id string) (*User, error) {
    req, err := http.NewRequestWithContext(ctx, "GET", "/users/"+id, nil)
    if err != nil {
        return nil, err
    }
    // ...
}

// Check context in loops
for _, item := range items {
    select {
    case <-ctx.Done():
        return ctx.Err()
    default:
        process(item)
    }
}

// Timeout context
ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
defer cancel()
result, err := fetchData(ctx)
```

## Concurrency

**Proverbs**:

- "Don't communicate by sharing memory, share memory by communicating"
- "Channels orchestrate; mutexes serialize"
- "Concurrency is not parallelism"

### Basic Patterns

```go
// WaitGroup for goroutine coordination
var wg sync.WaitGroup
for _, item := range items {
    wg.Add(1)
    go func(item Item) {
        defer wg.Done()
        process(item)
    }(item)
}
wg.Wait()

// Mutex for shared state
type SafeCounter struct {
    mu    sync.RWMutex
    count map[string]int
}

func (c *SafeCounter) Increment(key string) {
    c.mu.Lock()
    defer c.mu.Unlock()
    c.count[key]++
}
```

### Advanced Concurrency Patterns

**Worker Pool Pattern:**

```go
func ProcessWithWorkerPool(ctx context.Context, jobs []Job, numWorkers int) ([]Result, error) {
    jobChan := make(chan Job, len(jobs))
    resultChan := make(chan Result, len(jobs))

    // Start workers
    var wg sync.WaitGroup
    for i := 0; i < numWorkers; i++ {
        wg.Add(1)
        go func() {
            defer wg.Done()
            for job := range jobChan {
                select {
                case <-ctx.Done():
                    return
                default:
                    result := processJob(job)
                    resultChan <- result
                }
            }
        }()
    }

    // Send jobs
    go func() {
        defer close(jobChan)
        for _, job := range jobs {
            select {
            case <-ctx.Done():
                return
            case jobChan <- job:
            }
        }
    }()

    // Wait for workers and close results
    go func() {
        wg.Wait()
        close(resultChan)
    }()

    // Collect results
    var results []Result
    for result := range resultChan {
        results = append(results, result)
    }

    return results, nil
}
```

**Pipeline Pattern:**

```go
func ProcessPipeline(ctx context.Context, input <-chan Item) <-chan Result {
    stage1 := transformStage(ctx, input)
    stage2 := filterStage(ctx, stage1)
    stage3 := aggregateStage(ctx, stage2)
    return stage3
}

func transformStage(ctx context.Context, input <-chan Item) <-chan Transformed {
    output := make(chan Transformed)
    go func() {
        defer close(output)
        for item := range input {
            select {
            case <-ctx.Done():
                return
            case output <- transform(item):
            }
        }
    }()
    return output
}
```

**Semaphore Pattern:**

```go
type Semaphore struct {
    ch chan struct{}
}

func NewSemaphore(limit int) *Semaphore {
    return &Semaphore{
        ch: make(chan struct{}, limit),
    }
}

func (s *Semaphore) Acquire(ctx context.Context) error {
    select {
    case s.ch <- struct{}{}:
        return nil
    case <-ctx.Done():
        return ctx.Err()
    }
}

func (s *Semaphore) Release() {
    <-s.ch
}

// Usage
sem := NewSemaphore(10) // Max 10 concurrent operations
for _, item := range items {
    if err := sem.Acquire(ctx); err != nil {
        return err
    }
    go func(item Item) {
        defer sem.Release()
        process(item)
    }(item)
}
```

**Timeout Pattern:**

```go
func ProcessWithTimeout(ctx context.Context, duration time.Duration, fn func() error) error {
    ctx, cancel := context.WithTimeout(ctx, duration)
    defer cancel()

    done := make(chan error, 1)
    go func() {
        done <- fn()
    }()

    select {
    case err := <-done:
        return err
    case <-ctx.Done():
        return fmt.Errorf("operation timed out: %w", ctx.Err())
    }
}
```

**Bounded Channel Pattern:**

```go
func ProcessWithBackpressure(ctx context.Context, items []Item, bufferSize int) error {
    // Bounded channel prevents unbounded memory growth
    itemChan := make(chan Item, bufferSize)

    go func() {
        defer close(itemChan)
        for _, item := range items {
            select {
            case <-ctx.Done():
                return
            case itemChan <- item:
            }
        }
    }()

    for item := range itemChan {
        if err := process(item); err != nil {
            return err
        }
    }
    return nil
}
```

### Choose the Simplest Correct Primitive

**Rule**: Use channels for coordination/orchestration, mutexes for mutual exclusion.

```go
//  GOOD: Mutex for protecting shared state (serialization)
type SafeCounter struct {
    mu    sync.Mutex
    count int
}

func (c *SafeCounter) Increment() {
    c.mu.Lock()
    defer c.mu.Unlock()  // Always use defer
    c.count++
}

//  GOOD: Channel for communication/orchestration
func worker(jobs <-chan Job, results chan<- Result) {
    for job := range jobs {
        results <- process(job)
    }
}

//  GOOD: Channel for coordination (orchestration)
func processWithCoordination(ctx context.Context, items []Item) error {
    done := make(chan error, 1)
    go func() {
        // Process items
        done <- nil
    }()

    select {
    case err := <-done:
        return err
    case <-ctx.Done():
        return ctx.Err()
    }
}

//  BAD: Using channel for simple mutual exclusion
type Counter struct {

func (c *SafeCounter) Inc(key string) {
    c.mu.Lock()
    defer c.mu.Unlock()
    c.count[key]++
}

func (c *SafeCounter) Get(key string) int {
    c.mu.RLock()
    defer c.mu.RUnlock()
    return c.count[key]
}

// Channels for communication
results := make(chan Result, len(items))
for _, item := range items {
    go func(item Item) {
        results <- process(item)
    }(item)
}
for range items {
    result := <-results
    handle(result)
}
```

## Interfaces

```go
// Small, focused interfaces
type Reader interface {
    Read(p []byte) (n int, err error)
}

type Writer interface {
    Write(p []byte) (n int, err error)
}

// Compose interfaces
type ReadWriter interface {
    Reader
    Writer
}

// Accept interfaces, return structs
func ProcessData(r io.Reader) (*Result, error) {
    // ...
}
```

## Dependency Injection (DI) & Application Wiring

**Default (Go-idiomatic):** Prefer manual wiring at the composition root (`cmd/<app>/main.go`). Pass interfaces/structs explicitly via constructors.

Use a DI framework (e.g., `uber/fx`/`dig`, or compile-time `google/wire`) only when it clearly reduces risk/complexity, typically:

- Large dependency graphs changing frequently across teams
- Consistent lifecycle orchestration (start/stop ordering, cleanup) across modules
- Multiple servers/workers in one binary needing coordinated shutdown

If you adopt a DI framework:

- Keep framework usage at the edges (composition root); constructors remain plain Go
- Avoid “service locator” patterns (hidden dependencies); keep deps visible in constructors

## Testing

```go
// Table-driven tests
func TestParse(t *testing.T) {
    tests := []struct {
        name    string
        input   string
        want    int
        wantErr bool
    }{
        {"valid", "123", 123, false},
        {"negative", "-5", -5, false},
        {"invalid", "abc", 0, true},
    }
    
    for _, tt := range tests {
        t.Run(tt.name, func(t *testing.T) {
            got, err := Parse(tt.input)
            if (err != nil) != tt.wantErr {
                t.Errorf("Parse() error = %v, wantErr %v", err, tt.wantErr)
                return
            }
            if got != tt.want {
                t.Errorf("Parse() = %v, want %v", got, tt.want)
            }
        })
    }
}

// Subtests and parallelism
func TestAPI(t *testing.T) {
    t.Run("Create", func(t *testing.T) {
        t.Parallel()
        // ...
    })
    t.Run("Update", func(t *testing.T) {
        t.Parallel()
        // ...
    })
}
```

## HTTP Handlers

```go
// Handler with dependency injection
type UserHandler struct {
    userService UserService
    logger      *log.Logger
}

func (h *UserHandler) GetUser(w http.ResponseWriter, r *http.Request) {
    id := r.PathValue("id")
    user, err := h.userService.Get(r.Context(), id)
    if err != nil {
        http.Error(w, "User not found", http.StatusNotFound)
        return
    }
    json.NewEncoder(w).Encode(user)
}

// Middleware pattern
func LoggingMiddleware(next http.Handler) http.Handler {
    return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        start := time.Now()
        next.ServeHTTP(w, r)
        log.Printf("%s %s %v", r.Method, r.URL.Path, time.Since(start))
    })
}
```

## Struct Tags

```go
type User struct {
    ID        string    `json:"id" db:"id"`
    Name      string    `json:"name" db:"name" validate:"required"`
    Email     string    `json:"email" db:"email" validate:"email"`
    CreatedAt time.Time `json:"created_at" db:"created_at"`
}
```

## Generics (Go 1.18+)

```go
// Generic function
func Filter[T any](items []T, predicate func(T) bool) []T {
    result := make([]T, 0)
    for _, item := range items {
        if predicate(item) {
            result = append(result, item)
        }
    }
    return result
}

// Generic type with constraint
type Number interface {
    int | int64 | float64
}

func Sum[T Number](numbers []T) T {
    var sum T
    for _, n := range numbers {
        sum += n
    }
    return sum
}
```

## golangci-lint Configuration

```yaml
# .golangci.yml
linters:
  enable:
    - errcheck
    - gosimple
    - govet
    - ineffassign
    - staticcheck
    - unused
    - gosec
    - gofmt
    - goimports

linters-settings:
  errcheck:
    check-type-assertions: true
  govet:
    check-shadowing: true

issues:
  exclude-use-default: false
```
