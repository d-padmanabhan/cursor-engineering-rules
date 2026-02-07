# Cloudflare Patterns

## Naming & Terminology Consistency

- Never use `CloudFlare` anywhere (code/documentation). If found, fix to `Cloudflare`
- For Cloudflare, do not use the word `Domain`. Always use `Zone`. If any docs mention “Cloudflare Domain”, fix to “Cloudflare Zone”

## Rules language regex strings (raw vs quoted)

Cloudflare expressions support string values as either quoted strings (`"..."`) or raw strings (`r"..."`).
For regex patterns, prefer raw strings to reduce escaping mistakes (Cloudflare recommends this for regular expressions).

- **Quoted string**: backslashes are parsed by the string literal first, then by the regex engine - easy to under/over-escape
- **Raw string**: fewer escape surprises, easier to review

> [!NOTE]
> Case-insensitivity is separate. Use `(?i)` inside the regex (raw vs quoted does not control case sensitivity).
>
> Docs: `https://developers.cloudflare.com/ruleset-engine/rules-language/values/` (String values and regular expressions)

Example (raw regex + anchors):

```text
(http.host matches r"(?i)^citizen-dev[0-9]+\.sbx\.apps\.acme\.com\.?$" and ip.src in $firm_egress_ips)
```

## Workers

### Basic Worker

```javascript
export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);
    
    // Route handling
    if (url.pathname === '/api/users') {
      return handleUsers(request, env);
    }
    
    if (url.pathname === '/api/data') {
      return handleData(request, env);
    }
    
    return new Response('Not Found', { status: 404 });
  }
};

async function handleUsers(request, env) {
  // Access KV storage
  const users = await env.USERS_KV.get('all', 'json');
  
  return new Response(JSON.stringify(users), {
    headers: { 'Content-Type': 'application/json' }
  });
}

async function handleData(request, env) {
  // Access D1 database
  const { results } = await env.DB.prepare(
    'SELECT * FROM data WHERE active = ?'
  ).bind(true).all();
  
  return Response.json(results);
}
```

### Worker with Durable Objects

```javascript
export class Counter {
  constructor(state, env) {
    this.state = state;
  }

  async fetch(request) {
    let value = await this.state.storage.get('value') || 0;
    
    if (request.method === 'POST') {
      value++;
      await this.state.storage.put('value', value);
    }
    
    return new Response(value.toString());
  }
}

export default {
  async fetch(request, env) {
    const id = env.COUNTER.idFromName('global');
    const counter = env.COUNTER.get(id);
    return counter.fetch(request);
  }
};
```

## Pages

### Configuration (wrangler.toml)

```toml
name = "my-app"
compatibility_date = "2024-01-01"

[site]
bucket = "./dist"

[[kv_namespaces]]
binding = "KV"
id = "xxx"

[[d1_databases]]
binding = "DB"
database_name = "my-db"
database_id = "xxx"

[vars]
ENVIRONMENT = "production"
```

### Functions (Pages Functions)

```javascript
// functions/api/users.js
export async function onRequestGet(context) {
  const users = await context.env.DB.prepare(
    'SELECT id, name FROM users'
  ).all();
  
  return Response.json(users.results);
}

export async function onRequestPost(context) {
  const body = await context.request.json();
  
  await context.env.DB.prepare(
    'INSERT INTO users (name, email) VALUES (?, ?)'
  ).bind(body.name, body.email).run();
  
  return new Response('Created', { status: 201 });
}
```

## D1 Database

```javascript
// Create table
await env.DB.exec(`
  CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
  )
`);

// Insert
const result = await env.DB.prepare(
  'INSERT INTO users (name, email) VALUES (?, ?)'
).bind('Alice', 'alice@acme.com').run();

// Query
const { results } = await env.DB.prepare(
  'SELECT * FROM users WHERE email = ?'
).bind('alice@acme.com').all();

// Transaction (batch)
const batch = [
  env.DB.prepare('INSERT INTO users (name, email) VALUES (?, ?)').bind('Bob', 'bob@acme.com'),
  env.DB.prepare('INSERT INTO users (name, email) VALUES (?, ?)').bind('Carol', 'carol@acme.com'),
];
await env.DB.batch(batch);
```

## R2 Storage

```javascript
// Put object
await env.BUCKET.put('file.txt', 'Hello World', {
  httpMetadata: {
    contentType: 'text/plain'
  }
});

// Get object
const object = await env.BUCKET.get('file.txt');
if (object) {
  const text = await object.text();
  return new Response(text);
}

// List objects
const list = await env.BUCKET.list({ prefix: 'uploads/' });
for (const object of list.objects) {
  console.log(object.key);
}
```

## KV Storage

```javascript
// Put value
await env.KV.put('key', 'value', {
  expirationTtl: 3600  // 1 hour
});

// Put JSON
await env.KV.put('user:123', JSON.stringify({ name: 'Alice' }));

// Get value
const value = await env.KV.get('key');

// Get JSON
const user = await env.KV.get('user:123', 'json');

// Delete
await env.KV.delete('key');
```
