# Markdown & Mermaid

## Markdown Essentials

### Text Formatting

```markdown
**bold** or __bold__
*italic* or _italic_
~~strikethrough~~
`inline code`
```

### Block Quotes

```markdown
> This is a quote
> 
> - Author
```

### Task Lists

```markdown
- [x] Completed task
- [ ] Incomplete task
- [ ] Another task
```

### Collapsible Sections

```markdown
<details>
<summary>Click to expand</summary>

Hidden content here.

</details>
```

### Admonitions (GitHub)

```markdown
> [!NOTE]
> Information note

> [!TIP]
> Helpful tip

> [!WARNING]
> Warning message

> [!CAUTION]
> Critical warning
```

## Mermaid Diagrams

### Flowchart

```mermaid
flowchart TD
    A[Start] --> B{Is valid?}
    B -->|Yes| C[Process]
    B -->|No| D[Error]
    C --> E[End]
    D --> E
```

### GitHub Mermaid rendering pitfalls (common fixes)

#### Quote node labels that contain punctuation or `<br/>`

GitHub's Mermaid renderer can fail to parse some node labels containing characters like `(`, `)`, `,`, or HTML line breaks (`<br/>`) unless the label is quoted.

**Bad (can trigger parse errors on GitHub):**

```mermaid
flowchart TD
  A[Need to access an HTTP endpoint<br/>(web app, API, A2A, MCP)] --> B{Caller identity type?}
```

**Good (quote the label):**

```mermaid
flowchart TD
  A["Need to access an HTTP endpoint<br/>(web app, API, A2A, MCP)"] --> B{Caller identity type?}
```

#### Use Markdown links (not backticks) for clickable URLs

Canonical guidance: **800-markdown.mdc** → **Links and URLs** (global rule for all `.md` / `.mdx`).

In documentation, backticks render URLs as code and they are often **not clickable**.

- **Preferred**: `[AWS doc](https://docs.aws.amazon.com/vpc-lattice/latest/ug/auth-policies.html)`
- **Do not** wrap navigational URLs in backticks: `` `https://docs.aws.amazon.com/vpc-lattice/latest/ug/auth-policies.html` ``

### Sequence Diagram

```mermaid
sequenceDiagram
    autonumber
    participant C as Client
    participant S as Server
    participant D as Database
    
    C->>S: HTTP Request
    activate S
    S->>D: Query
    D-->>S: Results
    S-->>C: Response
    deactivate S
```

### Class Diagram

```mermaid
classDiagram
    class User {
        +String name
        +String email
        +login()
        +logout()
    }
    class Admin {
        +manageUsers()
    }
    User <|-- Admin
```

### State Diagram

```mermaid
stateDiagram-v2
    [*] --> Pending
    Pending --> Processing: start
    Processing --> Completed: finish
    Processing --> Failed: error
    Completed --> [*]
    Failed --> [*]
```

### Entity Relationship Diagram

```mermaid
erDiagram
    USER ||--o{ ORDER : places
    ORDER ||--|{ LINE_ITEM : contains
    PRODUCT ||--o{ LINE_ITEM : "is in"
    
    USER {
        int id PK
        string name
        string email UK
    }
    ORDER {
        int id PK
        int user_id FK
        date created_at
    }
```

### Gantt Chart

```mermaid
gantt
    title Project Timeline
    dateFormat  YYYY-MM-DD
    
    section Planning
    Requirements    :a1, 2024-01-01, 7d
    Design          :a2, after a1, 5d
    
    section Development
    Implementation  :b1, after a2, 14d
    Testing         :b2, after b1, 7d
```

### Pie Chart

```mermaid
pie title Traffic Sources
    "Organic" : 45
    "Direct" : 30
    "Referral" : 15
    "Social" : 10
```

## Diagram Best Practices

1. **Keep it simple**: Don't overcrowd
2. **Use consistent styling**: Same colors, shapes
3. **Add labels**: Make relationships clear
4. **Limit scope**: One diagram per concept
5. **Include in docs**: Diagrams should live near related text
