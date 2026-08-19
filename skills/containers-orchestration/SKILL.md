---
name: containers-orchestration
description: Docker and container best practices for production images, multi-stage builds, cache reuse, Docker Compose, health checks, scanning, publishing, and signing. Use when working with Dockerfiles, Containerfiles, Compose files, .dockerignore, image optimization, container security, docker push, Cosign, or Notation.
---

# Containers & Orchestration

## Guiding Principles

1. **Security First**: Non-root users, minimal base images, vulnerability scanning
2. **Efficiency**: Multi-stage builds, layer optimization, build cache
3. **Reproducibility**: Pin versions, explicit dependencies, deterministic builds
4. **Observability**: Health checks, proper logging, metrics endpoints

## Quick Reference

| Aspect | Standard |
|--------|----------|
| **Base Images** | Official image; pin the immutable digest for production |
| **Multi-Stage** | Required for compiled languages (Go, Rust, C++) |
| **User** | Run as non-root (use `USER node` or create user) |
| **Health Checks** | Include a meaningful `HEALTHCHECK` when the runtime exposes one |
| **Scanning** | Registry-native scanning gates (JFrog Xray / AWS ECR enhanced scanning) |
| **Signing** | Sign images with Sigstore/Cosign or Notation |

## Dockerfile Best Practices

### Use Official, Minimal Base Images

```dockerfile
# ✅ GOOD - Official, minimal, secure
FROM python:3.14-slim
FROM node:20-alpine

# ⭐ EXCELLENT - Distroless for production
FROM gcr.io/distroless/python3-debian12
FROM gcr.io/distroless/nodejs20-debian12

# ❌ AVOID - Large, unnecessary packages
FROM ubuntu:latest
```

### Pin Versions Explicitly

For production, pin the immutable digest (`image:tag@sha256:digest`) and use dependency automation for reviewed digest updates. The tag examples below are for readability and local development.

```dockerfile
# ✅ GOOD - Explicit version pinning
FROM python:3.14.0-slim-bookworm
FROM node:20.10.0-alpine3.19

# ❌ BAD - Unpredictable, non-reproducible
FROM python:latest
FROM node:alpine
```

### Multi-Stage Builds

**Go Example (Recommended Pattern):**

```dockerfile
# Build stage
FROM golang:1.25.0-alpine3.22 AS builder
WORKDIR /app

COPY go.mod go.sum ./
RUN go mod download

COPY . .
RUN CGO_ENABLED=0 GOOS=linux go build -a -installsuffix cgo -o main .

# Production stage - Distroless for minimal attack surface
FROM gcr.io/distroless/static-debian12
COPY --from=builder /app/main /main

USER nonroot:nonroot
EXPOSE 8080
ENTRYPOINT ["/main"]
```

**Python Example:**

```dockerfile
# Build stage
FROM python:3.14-slim AS builder
WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Production stage
FROM python:3.14-slim
WORKDIR /app

# Copy Python dependencies from builder
COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH

# Copy application code
COPY src/ ./src/

# Create non-root user
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app
USER appuser

EXPOSE 8000
CMD ["python", "-m", "src.main"]
```

## Layer Optimization

### Build Cache Gate (Non-Negotiable)

Optimize cache invalidation rather than minimizing the number of layers:

- Copy dependency manifests and lock files before application source.
- Install dependencies before broad source `COPY` instructions.
- Require `.dockerignore` coverage for volatile, generated, sensitive, and irrelevant files.
- Use multi-stage builds and copy only required runtime artifacts.
- Combine logically coupled package index, installation, and cleanup operations in one `RUN`.
- **Treat BuildKit cache mounts as performance-only.** Use them where supported, but require the build to succeed when the cache is empty or garbage-collected.
- Verify a repeated BuildKit build reports unchanged dependency copy and installation steps as cached. If building is unavailable, report that limitation instead of claiming verification.

Do not collapse stable dependency work and frequently changing application work merely to reduce the layer count. Detailed patterns are canonical in the Docker reference (`${HANDBOOK_ROOT}/skills/containers-orchestration/references/docker.md`); current cache behavior is documented in [Docker's cache guidance](https://docs.docker.com/build/cache/optimize/).

### Order Instructions by Change Frequency

```dockerfile
# ✅ GOOD - Least changing first, most changing last
FROM python:3.14-slim

# System dependencies (rarely change)
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Python dependencies (change occasionally)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Application code (changes frequently)
COPY src/ ./src/
```

### Use .dockerignore

```dockerignore
**/.git
**/.gitignore
**/.DS_Store
**/node_modules
**/dist
**/coverage
**/*.md
!README.md
**/.env
**/.env.*
**/Dockerfile*
**/docker-compose*.yml
**/.pytest_cache
**/__pycache__
**/*.pyc
**/.terraform
**/venv
**/.venv
**/logs
**/tmp
```

## Security Best Practices

### Run as Non-Root User

```dockerfile
FROM python:3.14-slim
WORKDIR /app

# Create non-root user
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Install dependencies as root
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Switch to non-root user
USER appuser

COPY --chown=appuser:appuser src/ ./src/
CMD ["python", "-m", "src.main"]
```

### Scan for Vulnerabilities

```bash
## Prefer registry-native scanning gates
#
# For container image vulnerability scanning, rely on a centralized scanner that
# runs in your registry / artifact-promotion pipeline (not ad-hoc on laptops):
#
# - JFrog Artifactory: JFrog Xray policies (block promotion/deploy on HIGH/CRITICAL)
# - AWS ECR: Enhanced scanning (Amazon Inspector) policies (block deploy on findings)
```

## Health Checks

### Application Health Check

```dockerfile
FROM python:3.14-slim
WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## Docker Compose Best Practices

### Production-Ready Compose File

```yaml
services:
  web:
    image: acme.com/webapp@sha256:${IMAGE_DIGEST:?set IMAGE_DIGEST}
    container_name: webapp
    restart: unless-stopped

    ports:
      - "8000:8000"

    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/mydb
      - REDIS_URL=redis://redis:6379
      - LOG_LEVEL=${LOG_LEVEL:-info}

    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_healthy

    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 5s
      retries: 3
      start_period: 10s

    networks:
      - backend

    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
        reservations:
          cpus: '1'
          memory: 1G

  db:
    image: postgres:16-alpine
    container_name: postgres
    restart: unless-stopped

    environment:
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD_FILE=/run/secrets/db_password
      - POSTGRES_DB=mydb

    secrets:
      - db_password

    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U user"]
      interval: 10s
      timeout: 5s
      retries: 5

    networks:
      - backend

    volumes:
      - postgres_data:/var/lib/postgresql/data

networks:
  backend:
    driver: bridge

volumes:
  postgres_data:
    driver: local

secrets:
  db_password:
    file: ./secrets/db_password.txt
```

## BuildKit Optimization

### Cache Mounts for Package Managers

**Python:**

```dockerfile
FROM python:3.14-slim
WORKDIR /app

COPY requirements.txt .

# Mount pip cache to speed up builds
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install -r requirements.txt

COPY src/ ./src/
CMD ["python", "-m", "src.main"]
```

**Node.js:**

```dockerfile
FROM node:20-alpine
WORKDIR /app

COPY package*.json ./

# Mount npm cache
RUN --mount=type=cache,target=/root/.npm \
    npm ci --only=production

COPY . .
CMD ["node", "index.js"]
```

## Dockerfile Review Checklist

- [ ] Pin all base image versions
- [ ] Use multi-stage builds for compiled languages
- [ ] Run as non-root user
- [ ] Use minimal base images (alpine, slim, distroless)
- [ ] Build cache gate passed with dependency inputs before application source
- [ ] Repeated build confirms unchanged dependency steps are cached, or limitation reported
- [ ] Combine logically coupled package-manager operations in one RUN
- [ ] Add `.dockerignore` file
- [ ] Include HEALTHCHECK instruction
- [ ] Clean up package manager caches
- [ ] Don't install unnecessary packages
- [ ] Use BuildKit cache mounts
- [ ] Scan for vulnerabilities
- [ ] Sign images for production

## Common Issues & Solutions

**Problem: Image is too large**

```bash
# Solution: Use multi-stage builds, alpine base, .dockerignore
docker images --format "{{.Repository}}:{{.Tag}}\t{{.Size}}"
docker history myapp:latest
```

**Problem: Slow builds**

```bash
# Solution: Order layers correctly, use cache mounts, BuildKit
export DOCKER_BUILDKIT=1
docker build --progress=plain -t myapp:latest .
```

**Problem: Container exits immediately**

```bash
# Debug: Override entrypoint
docker run --rm -it --entrypoint /bin/sh myapp:latest

# Check logs
docker logs <container_id>
```

## Detailed References

- **Docker Best Practices**: See references/docker.md (`${HANDBOOK_ROOT}/skills/containers-orchestration/references/docker.md`) for comprehensive Docker patterns, multi-stage builds, security, Compose, CI/CD integration, and troubleshooting
