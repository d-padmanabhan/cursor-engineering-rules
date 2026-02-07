# Makefile Patterns

## Basic Structure

```makefile
.PHONY: all build test clean help

# Default target
all: build test

# Variables
BINARY_NAME := myapp
GO_FILES := $(shell find . -name '*.go' -type f)
VERSION := $(shell git describe --tags --always --dirty)

# Build
build: $(GO_FILES)
 go build -ldflags="-X main.version=$(VERSION)" -o $(BINARY_NAME) .

# Test
test:
 go test -race -cover ./...

# Clean
clean:
 rm -f $(BINARY_NAME)
 rm -rf dist/

# Help
help:
 @echo "Available targets:"
 @echo "  build  - Build the binary"
 @echo "  test   - Run tests"
 @echo "  clean  - Remove build artifacts"
```

## Phony Targets

```makefile
.PHONY: build test lint format clean install

# Declare phony targets to avoid conflicts with files
# Phony targets are always executed regardless of file timestamps
```

## Variables

```makefile
# Simple assignment (evaluated at use time)
CC = gcc

# Immediate assignment (evaluated at definition time)
SOURCES := $(wildcard *.c)

# Conditional assignment (only if not already set)
PREFIX ?= /usr/local

# Append
CFLAGS += -Wall

# Environment variable with default
PORT ?= 8080
```

## Pattern Rules

```makefile
# Compile .c to .o
%.o: %.c
 $(CC) $(CFLAGS) -c $< -o $@

# Build executable from source
%: %.go
 go build -o $@ $<
```

## Functions

```makefile
# Get all Go files
GO_FILES := $(shell find . -name '*.go' -type f)

# Substitute extension
OBJECTS := $(SOURCES:.c=.o)

# Filter
TEST_FILES := $(filter %_test.go, $(GO_FILES))

# Wildcard
HEADERS := $(wildcard include/*.h)
```

## Conditional Logic

```makefile
ifeq ($(DEBUG), 1)
    CFLAGS += -g -DDEBUG
else
    CFLAGS += -O2
endif

ifdef VERBOSE
    Q :=
else
    Q := @
endif
```

## Multi-Target Recipes

```makefile
# Build for multiple platforms
PLATFORMS := linux-amd64 darwin-amd64 windows-amd64

.PHONY: release
release: $(addprefix dist/myapp-, $(PLATFORMS))

dist/myapp-%: $(GO_FILES)
 @mkdir -p dist
 GOOS=$(word 1,$(subst -, ,$*)) \
 GOARCH=$(word 2,$(subst -, ,$*)) \
 go build -o $@ .
```

## Docker Integration

```makefile
.PHONY: docker-build docker-push docker-run

IMAGE_NAME := myapp
IMAGE_TAG := $(VERSION)

docker-build:
 docker build -t $(IMAGE_NAME):$(IMAGE_TAG) .

docker-push: docker-build
 docker push $(IMAGE_NAME):$(IMAGE_TAG)

docker-run:
 docker run --rm -p 8080:8080 $(IMAGE_NAME):$(IMAGE_TAG)
```

## Help Target

```makefile
.PHONY: help
help: ## Show this help
 @grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
  sort | \
  awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

build: ## Build the application
 go build -o bin/app .

test: ## Run tests
 go test ./...

lint: ## Run linters
 golangci-lint run
```

## Best Practices

```makefile
# Use .PHONY for non-file targets
.PHONY: all build test clean

# Use automatic variables
# $@ - target name
# $< - first prerequisite
# $^ - all prerequisites
# $* - stem (pattern match)

# Suppress echoing with @
build:
 @echo "Building..."
 @go build -o bin/app .

# Use - to ignore errors
clean:
 -rm -rf dist/

# Group related targets
.PHONY: dev
dev: build test lint  ## Run development checks
```
