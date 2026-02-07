# AI/ML Integration

## LLM API Patterns

### Claude API

```python
import anthropic

client = anthropic.Anthropic()

message = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=1024,
    messages=[
        {"role": "user", "content": "Hello, Claude"}
    ]
)

print(message.content[0].text)
```

### Streaming

```python
with client.messages.stream(
    model="claude-sonnet-4-20250514",
    max_tokens=1024,
    messages=[{"role": "user", "content": "Write a story"}]
) as stream:
    for text in stream.text_stream:
        print(text, end="", flush=True)
```

### Tool Use

```python
tools = [
    {
        "name": "get_weather",
        "description": "Get current weather for a location",
        "input_schema": {
            "type": "object",
            "properties": {
                "location": {"type": "string"}
            },
            "required": ["location"]
        }
    }
]

message = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=1024,
    tools=tools,
    messages=[
        {"role": "user", "content": "What's the weather in London?"}
    ]
)

# Handle tool use
for block in message.content:
    if block.type == "tool_use":
        result = execute_tool(block.name, block.input)
        # Continue conversation with tool result
```

## Embedding Patterns

```python
# Generate embeddings
from openai import OpenAI

client = OpenAI()

response = client.embeddings.create(
    model="text-embedding-3-small",
    input="Hello world"
)

embedding = response.data[0].embedding

# Vector similarity search
import numpy as np

def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

# Find most similar documents
similarities = [
    cosine_similarity(query_embedding, doc_embedding)
    for doc_embedding in document_embeddings
]
```

## RAG Pattern

```python
from typing import List

async def retrieve_and_generate(query: str) -> str:
    # 1. Generate query embedding
    query_embedding = await generate_embedding(query)
    
    # 2. Search vector database
    relevant_docs = await vector_db.search(
        embedding=query_embedding,
        limit=5
    )
    
    # 3. Build context
    context = "\n\n".join([doc.content for doc in relevant_docs])
    
    # 4. Generate response
    response = await client.messages.create(
        model="claude-sonnet-4-20250514",
        messages=[
            {
                "role": "user",
                "content": f"""Based on the following context, answer the question.

Context:
{context}

Question: {query}"""
            }
        ]
    )
    
    return response.content[0].text
```

## Prompt Engineering

### System Prompts

```python
system_prompt = """You are a helpful assistant that answers questions about our product.

Guidelines:
- Be concise and accurate
- Cite sources when possible
- Say "I don't know" if uncertain
- Don't make up information
"""

message = client.messages.create(
    model="claude-sonnet-4-20250514",
    system=system_prompt,
    messages=[{"role": "user", "content": query}]
)
```

### Few-Shot Examples

```python
messages = [
    {"role": "user", "content": "Classify: I love this product!"},
    {"role": "assistant", "content": "positive"},
    {"role": "user", "content": "Classify: This is terrible."},
    {"role": "assistant", "content": "negative"},
    {"role": "user", "content": f"Classify: {user_input}"}
]
```

## Error Handling

```python
import anthropic

try:
    response = client.messages.create(...)
except anthropic.RateLimitError:
    # Implement backoff
    await asyncio.sleep(60)
    response = client.messages.create(...)
except anthropic.APIError as e:
    logger.error(f"API error: {e}")
    raise
```

## Caching

```python
from functools import lru_cache
import hashlib

@lru_cache(maxsize=1000)
def cached_embedding(text: str) -> list[float]:
    return generate_embedding(text)

def cache_key(messages: list) -> str:
    content = json.dumps(messages, sort_keys=True)
    return hashlib.sha256(content.encode()).hexdigest()
```

## Best Practices

1. **Rate limiting**: Respect API limits
2. **Caching**: Cache embeddings and responses when appropriate
3. **Streaming**: Use streaming for better UX
4. **Error handling**: Implement retries with backoff
5. **Logging**: Log prompts and responses for debugging
6. **Cost management**: Monitor token usage
7. **Testing**: Mock API calls in tests
