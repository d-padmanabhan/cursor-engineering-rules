# Shell Utilities & Documentation Ingestion

## Guiding Principle

Choose the lightest tool that reliably produces the content you need in a machine-consumable form.

- If the page is static HTML: prefer `curl` plus parsing (`jq` for JSON, HTML to text conversion, or a lightweight extractor).
- If the page is JavaScript-rendered or requires interaction: use a headless browser (Playwright).
- If Playwright is blocked or too heavy: try a doc-extraction proxy/cache (for example `https://context7.com/`) when it supports the target site.
- If you need diagrams understood (not OCR): use a screenshot (Playwright) and a vision-capable model (VLM).
- If you need text inside images: use OCR (Tesseract) as a supplement.
- If you are reading official documentation at scale: prefer a documentation-aware retrieval system (RAG) over raw scraping.

## Tool Selection Matrix

### 1) Static pages, APIs, feeds

Use these when content is already present in HTML or JSON without JS:

- `curl` for fetching
- `jq` for JSON shaping
- `ripgrep` for local searching
- `lynx -dump` for fast text extraction

Examples:

```bash
# Fetch HTML
curl -fsSL "https://acme.com/page" -o page.html

# Fetch JSON and shape it
curl -fsSL "https://api.acme.com/v1/items" | jq '.items[] | {id, name, updated_at}'

# Extract readable text quickly
lynx -dump -nolist "https://acme.com/page" > page.txt
```

When to stop here:

- If the text is good enough for the agent to answer questions
- If you do not need diagrams interpreted
- If the page is not JS-rendered

### 2) JS-heavy sites, auth flows, dynamic docs, robust extraction

Use Playwright when `curl` or `lynx` fails to capture the real content.

If Playwright fails (timeouts, bot protection, or brittle selectors) and you only need clean doc text, try a doc-extraction proxy/cache such as `https://context7.com/` (when it supports the target site).

Playwright is the right default for:

- SPA documentation sites
- Pages that lazy-load content
- Pages where you need to click "expand", "next", "load more"
- You need stable screenshots of diagrams

Operational guidance:

- Run headless by default
- Block heavy resources if you only need text (ads, video)
- Capture both:
  1. Extracted page text (DOM text)
  2. Screenshot of key sections (for diagrams)

### 3) Diagrams and visual reasoning

If the requirement is "understand the diagram", OCR is not enough.

Use:

- Playwright screenshot of the diagram region
- Vision-capable model (VLM) to interpret structure and meaning

Guidance for diagram prompting:

- Ask for components, flows, boundaries, assumptions
- Ask for a structured representation (bullets, adjacency list, Mermaid)
- Ask the model to cite what it sees in the image

### 4) OCR for text inside images

Use OCR only to extract text embedded in images, for example:

- A screenshot of a config snippet inside a PNG
- A diagram that has important labels but you only need the labels

Tool: Tesseract (OCR)

Guidance:

- Prefer higher resolution images
- Preprocess if needed (convert to grayscale, increase contrast)
- Treat OCR output as noisy and validate against surrounding text

### 5) Documentation retrieval systems (RAG-first)

When the goal is "read AWS, Cloudflare, Kubernetes docs reliably at scale", prefer a doc-aware retrieval approach.

Characteristics:

- Ingest official docs (site map, versioned docs, markdown sources)
- Chunk and index
- Retrieve only relevant sections per question
- Avoid scraping the same pages repeatedly

This is especially useful for:

- API references
- Configuration options
- Up-to-date product docs

Note: doc-extraction proxy/caching services (for example `https://context7.com/`) can be a pragmatic alternative when browser automation is blocked or too expensive for the use case.

## Quick Heuristics

### Prefer `lynx -dump` when

- You just need readable text quickly
- You are validating a URL manually
- You want a cheap baseline before heavier tooling

### Prefer `curl` when

- You need raw content for a parser
- You want deterministic fetches
- You are working with JSON endpoints

### Prefer Playwright when

- The site is JS-rendered
- The HTML contains placeholders and the real text loads later
- You need screenshots for diagrams
- You need to click, scroll, or expand sections

### Prefer Context7 (or similar) when

- Playwright is blocked by bot protection or is too expensive for the task
- You only need clean, readable documentation text (not interaction)
- The target documentation source is supported by the retrieval/proxy system

### Prefer VLM screenshot analysis when

- "Understand the diagram" is a core requirement
- The meaning is in arrows, layout, grouping, icons, or visual structure

### Prefer OCR when

- The only missing piece is text inside an image
- You do not need structural understanding

## Anti-patterns (what NOT to do)

### Do not default to a headless browser for everything

Headless browsers are heavier and slower. Use them when necessary.

Bad:

- Always use a browser to fetch a static blog post

Good:

- Try `lynx -dump` or `curl` first, then escalate to Playwright if needed

### Do not paste entire pages into the LLM

Instead:

- Extract main content
- Keep headings
- Strip nav, footers, cookie banners
- Chunk into reasonable sections

### Do not scrape aggressively

- Respect robots.txt and site policies
- Add rate limiting
- Cache responses

## Common Commands Reference

### lynx

```bash
lynx -dump -nolist "https://acme.com"
lynx -source "https://acme.com" > page.html
```

### curl

```bash
curl -fsSL "https://acme.com" -o page.html
curl -I "https://acme.com"
```

### jq

```bash
cat payload.json | jq '.'
curl -fsSL "https://api.acme.com" | jq '.items[] | {id, name}'
```

### httpie

**Advanced httpie usage:**

```bash
# GET request
http GET "https://api.acme.com/v1/items"

# GET with headers
http GET "https://api.acme.com/v1/items" \
    Authorization:"Bearer $TOKEN" \
    Accept:"application/json"

# POST JSON
http POST "https://api.acme.com/v1/items" \
    name="Item Name" \
    description="Item description"

# POST from file
http POST "https://api.acme.com/v1/items" < payload.json

# PUT request
http PUT "https://api.acme.com/v1/items/123" \
    name="Updated Name"

# DELETE request
http DELETE "https://api.acme.com/v1/items/123" \
    Authorization:"Bearer $TOKEN"

# Query parameters
http GET "https://api.acme.com/v1/items" \
    page==1 \
    limit==10 \
    sort==created_at

# Form data
http --form POST "https://api.acme.com/v1/upload" \
    file@document.pdf \
    description="My document"

# Download file
http --download GET "https://api.acme.com/files/document.pdf"

# Follow redirects
http --follow GET "https://api.acme.com/redirect"

# Save response to file
http GET "https://api.acme.com/v1/items" > response.json

# Pretty print JSON response
http GET "https://api.acme.com/v1/items" | jq '.'

# Verbose output (headers, request/response)
http -v GET "https://api.acme.com/v1/items"

# Check status only
http --check-status GET "https://api.acme.com/v1/items"

# Timeout
http --timeout=5 GET "https://api.acme.com/v1/items"

# Custom user agent
http GET "https://api.acme.com/v1/items" \
    User-Agent:"MyApp/1.0"
```

### ripgrep

**Advanced ripgrep patterns:**

```bash
# Basic search
rg "pattern" path/

# With line numbers
rg -n "pattern" path/

# Case-insensitive
rg -i "pattern" path/

# Show context (before/after lines)
rg -C 3 "pattern" path/        # 3 lines before and after
rg -B 2 -A 2 "pattern" path/   # 2 before, 2 after

# Search in specific file types
rg -t py "pattern"             # Python files only
rg -t js -t ts "pattern"       # JavaScript and TypeScript

# Exclude patterns
rg "pattern" --glob "!*.min.js"  # Exclude minified files
rg "pattern" -g "!node_modules/**" # Exclude directories

# Count matches
rg -c "pattern" path/          # Count per file
rg --count-matches "pattern"   # Total count

# Only show filenames
rg -l "pattern" path/          # Files with matches
rg -L "pattern" path/          # Files without matches

# Multiline search
rg -U "pattern1.*\n.*pattern2" path/

# Replace (with preview)
rg "old" -r "new" path/        # Preview replacements
rg "old" -r "new" --replace path/  # Actually replace

# JSON output
rg --json "pattern" path/      # Machine-readable output

# Complex patterns
rg "VPC Lattice|PrivateLink|Cloudflare Tunnel" docs/
rg "error|warning|critical" -i log.txt
rg "\b\d{3}-\d{2}-\d{4}\b"    # SSN pattern (example)
```

# Shell Utilities

## curl

```bash
# GET request with headers
curl -sS -H "Authorization: Bearer $TOKEN" \
    "https://api.acme.com/users"

# POST JSON
curl -sS -X POST \
    -H "Content-Type: application/json" \
    -d '{"name": "Alice"}' \
    "https://api.acme.com/users"

# Download file
curl -sS -L -o output.zip "https://example.com/file.zip"

# With retry
curl -sS --retry 3 --retry-delay 2 "https://api.acme.com/health"

# Silent with error handling
response=$(curl -sS -w "\n%{http_code}" "https://api.acme.com/users")
http_code=$(echo "$response" | tail -1)
body=$(echo "$response" | head -n -1)
[[ "$http_code" == "200" ]] || die "Request failed: $http_code"
```

## jq

```bash
# Extract field
echo '{"name": "Alice"}' | jq -r '.name'  # Alice

# Filter array
echo '[{"age": 25}, {"age": 35}]' | jq '.[] | select(.age > 30)'

# Transform data
echo '{"users": [{"name": "Alice"}]}' | jq '.users[].name'

# Create new structure
echo '{"a": 1, "b": 2}' | jq '{sum: (.a + .b)}'

# With variables
jq --arg name "$USER_NAME" '.users[] | select(.name == $name)' data.json

# Compact output
jq -c '.' data.json

# Raw output (no quotes)
jq -r '.id' data.json
```

## awk

```bash
# Print specific column
awk '{print $2}' file.txt

# Sum column
awk '{sum += $1} END {print sum}' numbers.txt

# Filter by pattern
awk '/ERROR/ {print $0}' log.txt

# Field separator
awk -F',' '{print $1, $3}' data.csv

# Variables
awk -v threshold=100 '$1 > threshold {print}' data.txt
```

## sed

```bash
# Replace text
sed 's/old/new/g' file.txt

# In-place edit
sed -i 's/old/new/g' file.txt

# Delete lines matching pattern
sed '/pattern/d' file.txt

# Print specific lines
sed -n '5,10p' file.txt
```

## grep

```bash
# Search recursively
grep -r "pattern" ./src

# Show line numbers
grep -n "ERROR" log.txt

# Invert match
grep -v "DEBUG" log.txt

# Extended regex
grep -E "error|warning" log.txt

# Only filenames
grep -l "TODO" *.py

# Count matches
grep -c "pattern" file.txt
```

## find

```bash
# Find by name
find . -name "*.py" -type f

# Find and execute
find . -name "*.log" -type f -exec rm {} \;

# Find by modification time
find . -mtime -7 -type f  # Modified in last 7 days

# Exclude directories
find . -name "*.js" -not -path "./node_modules/*"

# Find empty files
find . -empty -type f
```

## xargs

```bash
# Parallel execution
find . -name "*.txt" | xargs -P 4 -I {} process {}

# With null separator (handles spaces)
find . -name "*.txt" -print0 | xargs -0 wc -l

# Limit arguments per command
echo "1 2 3 4 5" | xargs -n 2 echo
```

## Combining Tools

```bash
# Get unique users from JSON API
curl -sS "https://api.acme.com/logs" | \
    jq -r '.[].user' | \
    sort -u

# Count files by extension
find . -type f | \
    sed 's/.*\.//' | \
    sort | \
    uniq -c | \
    sort -rn

# Process CSV with error handling
while IFS=',' read -r name email; do
    [[ "$name" == "name" ]] && continue  # Skip header
    echo "Processing: $name <$email>"
done < users.csv
```

## fzf (fuzzy finder)

Interactive fuzzy finder for command-line productivity:

```bash
# File search (Ctrl+T)
# Type partial filename, fzf filters results as you type

# Command history (Ctrl+R)
# Search through shell history interactively

# Directory navigation (Alt+C)
# Change directory with fuzzy search

# Git workflows
git checkout $(git branch | fzf)        # Switch branches
git log --oneline | fzf                 # Browse commits
git diff $(git diff --name-only | fzf)  # View diff of selected file

# Process management
kill -9 $(ps aux | fzf | awk '{print $2}')  # Kill process interactively

# Code search integration
rg "pattern" | fzf  # Search code, then filter results
```

**Shell integration setup:**

```bash
# Install shell bindings (adds Ctrl+R, Ctrl+T, Alt+C)
$(brew --prefix)/opt/fzf/install
```

**Use cases:**

- Finding files quickly without typing full paths
- Searching command history efficiently
- Navigating large directory structures
- Enhancing git workflows with interactive selection
- Filtering command output interactively

---

## Progressive Escalation Strategy

When reading documentation or web content, follow this escalation path:

### Level 1: Static Content (Fastest)

**Tools:** `curl`, `lynx`, `jq`

```bash
# Try curl first
curl -fsSL "https://docs.acme.com/page" | lynx -stdin -dump

# If JSON API
curl -fsSL "https://api.acme.com/docs" | jq '.content'
```

**When to stop:** Content is complete, no JS needed, no diagrams.

### Level 2: JavaScript-Rendered Content

**Tools:** Playwright (headless browser)

```python
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto("https://docs.acme.com/page")
    content = page.content()
    browser.close()
```

**When to use:** Content loads via JS, lazy-loaded sections, SPA docs.

**When to stop:** Content extracted successfully.

### Level 3: Bot Protection / Blocked

**Tools:** Context7 or similar doc-extraction proxy

```bash
# Use proxy service when Playwright is blocked
curl "https://context7.com/extract?url=https://docs.acme.com/page"
```

**When to use:** Playwright blocked, only need clean text, proxy supports site.

**When to stop:** Content retrieved successfully.

### Level 4: Diagrams and Visual Content

**Tools:** Playwright (screenshot) + Vision Language Model (VLM)

```python
# Take screenshot
page.screenshot(path="diagram.png", clip={"x": 100, "y": 100, "width": 800, "height": 600})

# Analyze with VLM
# Prompt: "Describe this diagram, identify components, flows, and relationships"
```

**When to use:** Need to understand visual structure, diagrams, flowcharts.

**When to stop:** Diagram understood and documented.

### Level 5: Text in Images

**Tools:** OCR (Tesseract)

```bash
# Extract text from image
tesseract diagram.png output.txt

# With preprocessing
convert diagram.png -grayscale -contrast-stretch 0% diagram_processed.png
tesseract diagram_processed.png output.txt
```

**When to use:** Only need text labels from images, not structural understanding.

**When to stop:** Text extracted successfully.

### Level 6: Official Documentation at Scale

**Tools:** RAG (Retrieval-Augmented Generation) system

**Characteristics:**

- Pre-indexed documentation
- Chunked and searchable
- Retrieves only relevant sections
- Avoids repeated scraping

**When to use:** Reading AWS, Cloudflare, Kubernetes docs repeatedly, need up-to-date info.

**When to stop:** Relevant sections retrieved.

### Escalation Decision Tree

```
Start: Need to read documentation
  │
  ├─ Is content static HTML? → Use curl/lynx
  │     │
  │     └─ Success? → Done
  │     └─ Failed? → Escalate to Level 2
  │
  ├─ Is content JS-rendered? → Use Playwright
  │     │
  │     ├─ Need diagrams? → Use Playwright + VLM (Level 4)
  │     ├─ Blocked by bot protection? → Use Context7 (Level 3)
  │     └─ Success? → Done
  │
  ├─ Need text from images? → Use OCR (Level 5)
  │     │
  │     └─ Success? → Done
  │
  └─ Reading official docs repeatedly? → Use RAG (Level 6)
        │
        └─ Success? → Done
```

### Rate Limiting and Caching

**Always implement:**

```bash
# Rate limiting
sleep 1  # Wait 1 second between requests

# Caching
if [[ ! -f "cache/page.html" ]]; then
    curl -fsSL "https://docs.acme.com/page" > cache/page.html
fi
cat cache/page.html
```

**Best Practices:**

- Cache responses locally
- Respect `robots.txt`
- Add delays between requests (1-2 seconds)
- Use conditional requests (`If-Modified-Since` header)
- Set reasonable timeouts

---

## Documentation Retrieval Systems (RAG-First)

When the goal is "read AWS, Cloudflare, Kubernetes docs reliably at scale", prefer a doc-aware retrieval approach.

### Characteristics

- **Pre-indexed:** Official docs ingested and indexed
- **Chunked:** Content split into searchable sections
- **Retrieval-only:** Load only relevant sections per query
- **Avoids scraping:** No repeated page fetches
- **Up-to-date:** Can sync with official sources

### When to Use RAG

- Reading official documentation repeatedly
- Need up-to-date API references
- Configuration options lookup
- Product documentation queries
- Avoiding rate limits from scraping

### Chunking Strategy

**For documentation:**

- **Size:** 500-1000 tokens per chunk
- **Overlap:** 50-100 tokens between chunks
- **Boundaries:** Respect section headings, code blocks
- **Metadata:** Include URL, section title, page number

**Example chunk structure:**

```json
{
  "content": "## AWS S3 Bucket Configuration\n\n...",
  "metadata": {
    "url": "https://docs.aws.amazon.com/s3/latest/userguide/...",
    "section": "Bucket Configuration",
    "page": 1,
    "chunk_id": "s3-config-001"
  }
}
```

### Indexing Strategy

1. **Crawl official docs** - Use sitemap or doc index
2. **Extract content** - Clean HTML, preserve structure
3. **Chunk intelligently** - Respect semantic boundaries
4. **Generate embeddings** - Vector representations
5. **Store in vector DB** - Pinecone, Weaviate, Qdrant
6. **Sync periodically** - Update when docs change

### Retrieval Process

1. **Query embedding** - Convert question to vector
2. **Similarity search** - Find relevant chunks
3. **Rerank** - Score and filter results
4. **Return top-k** - Most relevant chunks
5. **Format for LLM** - Add citations, context

### Anti-Patterns

**Don't:**

- Scrape the same docs repeatedly
- Load entire documentation sets into context
- Ignore version information
- Skip citation/attribution
- Use stale documentation

**Do:**

- Use RAG for official docs
- Cache retrieval results
- Include source URLs
- Verify documentation versions
- Update indexes regularly

---

## Modern CLI Tools

### fd (fast find alternative)

Fast, user-friendly alternative to `find` written in Rust:

```bash
# Find files by name (case-insensitive by default)
fd "\.py$"                    # Find all Python files
fd "test"                     # Find files/dirs containing "test"
fd -e py                      # Find files with .py extension
fd -e py -e js                # Find .py or .js files

# Search in specific directory
fd "config" src/              # Find "config" in src/ directory

# Case-sensitive search
fd -s "Config"                # Case-sensitive search

# Find directories only
fd -t d "test"                # Find directories named "test"
fd -t f "test"                # Find files only (default)

# Exclude patterns
fd -e py --exclude "venv"     # Find .py files, exclude venv/
fd -E "*.pyc" -E "__pycache__"  # Exclude multiple patterns

# Execute commands on results
fd -e py -x python            # Run python on each .py file
fd -e sh -x chmod +x          # Make shell scripts executable

# Limit depth
fd --max-depth 2 "test"       # Search max 2 levels deep

# Common use cases
fd "\.tf$"                    # Find Terraform files
fd "README"                   # Find README files
fd -e yaml -e yml             # Find YAML files
fd "\.git" -t d               # Find .git directories
```

**Advantages over `find`:**

- Faster (written in Rust)
- Simpler syntax (no need for `-name`, `-type` flags)
- Case-insensitive by default
- Respects `.gitignore` automatically
- Colorized output
- Parallel execution

**Migration from find:**

```bash
# find equivalent
find . -name "*.py" -type f
# fd equivalent
fd -e py -t f

# find equivalent
find . -maxdepth 2 -name "test*"
# fd equivalent
fd --max-depth 2 "test"
```

---

### fzf (fuzzy finder)

Interactive fuzzy finder for command-line productivity:

```bash
# File search (Ctrl+T)
# Type partial filename, fzf filters results as you type

# Command history (Ctrl+R)
# Search through shell history interactively

# Directory navigation (Alt+C)
# Change directory with fuzzy search

# Git workflows
git checkout $(git branch | fzf)              # Switch branches
git log --oneline | fzf                        # Browse commits
git diff $(git diff --name-only | fzf)         # View diff of selected file

# Process management
kill -9 $(ps aux | fzf | awk '{print $2}')     # Kill process interactively

# Code search integration
rg "pattern" | fzf                             # Search code, then filter results
```

**Shell integration setup:**

```bash
# Install shell bindings (adds Ctrl+R, Ctrl+T, Alt+C)
$(brew --prefix)/opt/fzf/install
```

**Use cases:**

- Finding files quickly without typing full paths
- Searching command history efficiently
- Navigating large directory structures
- Enhancing git workflows with interactive selection
- Filtering command output interactively

---

## Resources

- [awesome-tuis](https://github.com/rothgar/awesome-tuis) - Curated list of TUI applications for terminal productivity (dashboards, file managers, git tools, database clients, etc.)
- [zoxide](https://github.com/ajeetdsouza/zoxide) - Smarter cd command that learns your habits
- [tmux](https://github.com/tmux/tmux) - Terminal multiplexer for persistent sessions
- [gh](https://cli.github.com/) - GitHub CLI for issues, PRs, and repo management
- [stow](https://www.gnu.org/software/stow/) - Symlink farm manager (great for dotfiles)
