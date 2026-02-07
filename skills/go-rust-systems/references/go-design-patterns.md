# Go Design Patterns

## Factory Pattern

```go
// Database connection factory
type DatabaseType string

const (
    Postgres DatabaseType = "postgres"
    MySQL    DatabaseType = "mysql"
)

type Database interface {
    Query(ctx context.Context, sql string) ([]map[string]interface{}, error)
    Close() error
}

type PostgresDB struct {
    conn *sql.DB
}

func (p *PostgresDB) Query(ctx context.Context, sql string) ([]map[string]interface{}, error) {
    rows, err := p.conn.QueryContext(ctx, sql)
    if err != nil {
        return nil, err
    }
    defer rows.Close()
    // Process rows...
    return nil, nil
}

func (p *PostgresDB) Close() error {
    return p.conn.Close()
}

type MySQLDB struct {
    conn *sql.DB
}

func (m *MySQLDB) Query(ctx context.Context, sql string) ([]map[string]interface{}, error) {
    // MySQL-specific implementation
    return nil, nil
}

func (m *MySQLDB) Close() error {
    return m.conn.Close()
}

func NewDatabase(dbType DatabaseType, dsn string) (Database, error) {
    switch dbType {
    case Postgres:
        conn, err := sql.Open("postgres", dsn)
        if err != nil {
            return nil, err
        }
        return &PostgresDB{conn: conn}, nil
    case MySQL:
        conn, err := sql.Open("mysql", dsn)
        if err != nil {
            return nil, err
        }
        return &MySQLDB{conn: conn}, nil
    default:
        return nil, fmt.Errorf("unsupported database type: %s", dbType)
    }
}
```

## Strategy Pattern

```go
// Deployment strategy
type DeploymentStrategy interface {
    Deploy(ctx context.Context, app string) error
}

type DevelopmentDeployment struct{}

func (d *DevelopmentDeployment) Deploy(ctx context.Context, app string) error {
    fmt.Printf("Deploying %s to dev (single instance)\n", app)
    return nil
}

type ProductionDeployment struct{}

func (p *ProductionDeployment) Deploy(ctx context.Context, app string) error {
    fmt.Printf("Deploying %s to prod (multi-AZ, auto-scaling)\n", app)
    return nil
}

type DeploymentContext struct {
    strategy DeploymentStrategy
}

func NewDeploymentContext(strategy DeploymentStrategy) *DeploymentContext {
    return &DeploymentContext{strategy: strategy}
}

func (dc *DeploymentContext) Execute(ctx context.Context, app string) error {
    return dc.strategy.Deploy(ctx, app)
}
```

## Observer Pattern

```go
type Event string

const (
    UserCreated Event = "user.created"
    UserUpdated Event = "user.updated"
)

type EventHandler interface {
    Handle(ctx context.Context, event Event, data interface{}) error
}

type EventBus struct {
    handlers map[Event][]EventHandler
    mu       sync.RWMutex
}

func NewEventBus() *EventBus {
    return &EventBus{
        handlers: make(map[Event][]EventHandler),
    }
}

func (eb *EventBus) Subscribe(event Event, handler EventHandler) {
    eb.mu.Lock()
    defer eb.mu.Unlock()
    eb.handlers[event] = append(eb.handlers[event], handler)
}

func (eb *EventBus) Publish(ctx context.Context, event Event, data interface{}) error {
    eb.mu.RLock()
    handlers := eb.handlers[event]
    eb.mu.RUnlock()

    for _, handler := range handlers {
        if err := handler.Handle(ctx, event, data); err != nil {
            return fmt.Errorf("handler failed: %w", err)
        }
    }
    return nil
}
```
