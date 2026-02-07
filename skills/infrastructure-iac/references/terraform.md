# Terraform Engineering Patterns

**Goal:** Secure-by-default, efficient, modular Terraform with strong validation, documentation, and CI hygiene.

## Terraform Philosophy

**Core Principles:**

- **"Infrastructure as Code, not Infrastructure as Config"** - Terraform is code; treat it with same rigor as application code
- **"State is the source of truth"** - Protect state, version it, back it up, lock it
- **"Idempotency is non-negotiable"** - Same input should produce same output, safe to run multiple times
- **"Modules over copy-paste"** - Reusable, composable modules reduce errors and maintenance
- **"Validate early, fail fast"** - Use validations, preconditions, postconditions to catch errors early
- **"Security by default"** - Least privilege IAM, encryption everywhere, no secrets in code
- **"Explicit over implicit"** - Clear dependencies, explicit providers, documented assumptions

**Applying Principles:**

```hcl
# BAD: Implicit, insecure, fragile
resource "aws_instance" "web" {
  ami           = "ami-12345"
  instance_type = "t2.micro"
}

# GOOD: Explicit, secure, validated
variable "environment" {
  type        = string
  description = "Deployment environment"
  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "Environment must be dev, staging, or prod."
  }
}

resource "aws_instance" "web" {
  ami           = data.aws_ami.ubuntu.id
  instance_type = var.instance_type

  vpc_security_group_ids = [aws_security_group.web.id]
  subnet_id              = aws_subnet.public["az-a"].id

  tags = merge(
    local.common_tags,
    {
      Name = "${var.app}-${var.environment}-web"
    }
  )

  lifecycle {
    create_before_destroy = true
    prevent_destroy       = var.environment == "prod"
  }
}
```

---

## Quick Reference

### Essential Commands

> [!CAUTION]
> **Remote/stateful operations:** `terraform apply` / `terraform destroy` change real infrastructure and state.
> Run only with explicit approval; prefer `terraform plan` and review output first.

```bash
# Initialization & Planning
terraform init                          # Initialize working directory
terraform init -upgrade                 # Upgrade providers to latest allowed version
terraform plan                          # Preview changes
terraform plan -out=tfplan              # Save plan for apply
terraform plan -target=module.vpc       # Plan specific resource/module

# Apply & Destroy
terraform apply tfplan                  # Apply saved plan
terraform apply -auto-approve           # Apply without confirmation (CI only!)
terraform destroy -target=resource.name # Destroy specific resource

# State Management
terraform state list                    # List resources in state
terraform state show aws_vpc.this       # Show specific resource details
terraform state mv src dest             # Rename/move resource in state
terraform state rm resource.name        # Remove from state (doesn't destroy)
terraform state pull > backup.tfstate   # Backup state locally

# Import & Validation
terraform import aws_vpc.this vpc-12345 # Import existing resource
terraform validate                      # Validate configuration
terraform fmt -check -recursive         # Check formatting
terraform fmt -recursive                # Format all files

# Troubleshooting
terraform refresh                       # Sync state with real infrastructure
terraform apply -refresh-only           # Safer alternative to refresh
terraform force-unlock LOCK_ID          # Unlock stuck state
TF_LOG=DEBUG terraform apply            # Enable debug logging
```

### Critical Patterns

```hcl
# 1. Prefer for_each for stability
resource "aws_subnet" "private" {
  for_each = var.private_subnets  # Use map/set keys for stable addressing
  # NOT: count = length(var.private_subnets)
}

# 2. Pin provider versions
terraform {
  required_version = ">= 1.12.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.0"
    }
  }
}

# 3. Validate inputs aggressively
variable "environment" {
  type = string
  validation {
    condition     = can(regex("^(dev|staging|prod)$", var.environment))
    error_message = "environment must be one of: dev, staging, prod."
  }
}

# 4. Mark sensitive data
variable "db_password" {
  type      = string
  sensitive = true
}

# 5. Use lifecycle for critical resources
resource "aws_s3_bucket" "state" {
  lifecycle {
    prevent_destroy = true
  }
}
```

---

## Project Structure

```
terraform/
├── versions.tf       # Terraform & provider versions
├── providers.tf      # Provider configurations
├── main.tf           # Root module resources
├── variables.tf      # Input variables
├── outputs.tf        # Output values
├── locals.tf         # Local values
├── data.tf           # Data sources
├── backend.tf        # State backend config
├── README.md         # Module documentation
└── modules/
    └── vpc/
        ├── main.tf
        ├── variables.tf
        ├── outputs.tf
        └── README.md
```

---

## Naming & Formatting

### Naming Conventions

- **HCL labels**: `snake_case` for resource/module/variable/output names
- **Cloud names/tags**: use `kebab-case` (e.g., `Name = "app-core-vpc"`)
- **Files**: conventional layout (versions.tf, providers.tf, main.tf, etc.)

### Tagging Strategy

```hcl
locals {
  base_tags = {
    app         = var.app
    environment = var.environment
    owner       = var.owner
    managed_by  = "terraform"
  }
}

resource "aws_vpc" "this" {
  cidr_block           = var.vpc_cidr
  enable_dns_support   = true
  enable_dns_hostnames = true
  tags                 = merge(local.base_tags, { Name = "${var.app}-${var.environment}-vpc" })
}
```

---

## for_each vs count

### Prefer for_each for Stable Addressing

```hcl
# ✅ GOOD: Stable addressing with for_each
resource "aws_subnet" "private" {
  for_each          = var.private_subnets  # map(string) with keys like "az-a", "az-b"
  vpc_id            = aws_vpc.this.id
  cidr_block        = each.value
  availability_zone = "${var.region}${each.key}"
  tags              = { Name = "${var.app}-${each.key}-private" }
}

# ❌ BAD: count makes addressing fragile
resource "aws_subnet" "private" {
  count             = length(var.private_subnets)  # Reordering list breaks state
  vpc_id            = aws_vpc.this.id
  cidr_block        = var.private_subnets[count.index]
}
```

---

## Advanced Patterns

### For-Expressions

```hcl
# Transform list to map
locals {
  subnet_map = {
    for idx, subnet in var.subnets : "subnet-${idx}" => subnet
  }
}

# Filter and transform
locals {
  public_subnets = {
    for k, v in aws_subnet.this : k => v.id
    if v.map_public_ip_on_launch == true
  }
}

# Complex transformations
locals {
  security_group_rules = flatten([
    for sg_id, sg_config in var.security_groups : [
      for rule in sg_config.rules : {
        security_group_id = sg_id
        type              = rule.type
        from_port         = rule.from_port
        to_port           = rule.to_port
        protocol          = rule.protocol
        cidr_blocks       = rule.cidr_blocks
      }
    ]
  ])
}
```

### Dynamic Blocks

```hcl
resource "aws_security_group" "web" {
  name        = "${var.app}-web-sg"
  description = "Security group for web servers"
  vpc_id      = aws_vpc.this.id

  dynamic "ingress" {
    for_each = var.allowed_ports
    content {
      from_port   = ingress.value
      to_port     = ingress.value
      protocol    = "tcp"
      cidr_blocks = [var.allowed_cidr]
    }
  }

  dynamic "egress" {
    for_each = var.egress_rules
    content {
      from_port   = egress.value.from_port
      to_port     = egress.value.to_port
      protocol    = egress.value.protocol
      cidr_blocks = egress.value.cidr_blocks
    }
  }
}
```

### Function Composition

```hcl
# Safe defaults with try/coalesce
locals {
  instance_type = try(
    var.instance_type,
    coalesce(
      var.environment == "prod" ? "m5.large" : null,
      var.environment == "staging" ? "t3.medium" : null,
      "t3.micro"
    )
  )
}

# String manipulation
locals {
  normalized_name = lower(replace(var.name, " ", "-"))
  tags = merge(
    var.common_tags,
    {
      Name = "${var.prefix}-${local.normalized_name}"
    }
  )
}
```

---

## Module Best Practices

### Module Structure

```hcl
# modules/vpc/variables.tf
variable "vpc_cidr" {
  type        = string
  description = "CIDR block for VPC"

  validation {
    condition     = can(cidrhost(var.vpc_cidr, 0))
    error_message = "Must be valid CIDR."
  }
}

# modules/vpc/main.tf
resource "aws_vpc" "this" {
  cidr_block           = var.vpc_cidr
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = merge(var.tags, {
    Name = "${var.name}-vpc"
  })
}

# modules/vpc/outputs.tf
output "vpc_id" {
  description = "VPC ID"
  value       = aws_vpc.this.id
}
```

### Module Composition

```hcl
# environments/production/main.tf
module "vpc" {
  source = "../../modules/vpc"

  vpc_cidr = "10.0.0.0/16"
  name     = "prod"
  tags     = local.common_tags
}

module "eks" {
  source = "../../modules/eks"

  vpc_id     = module.vpc.vpc_id
  subnet_ids = module.vpc.private_subnet_ids
}
```

---

## Validation & Conditions

### Input Validation

```hcl
variable "environment" {
  description = "Deployment environment (e.g., dev, staging, prod)."
  type        = string
  validation {
    condition     = can(regex("^(dev|staging|prod)$", var.environment))
    error_message = "environment must be one of: dev, staging, prod."
  }
}

variable "vpc_cidr" {
  description = "VPC CIDR block"
  type        = string
  validation {
    condition     = can(cidrhost(var.vpc_cidr, 0))
    error_message = "Must be a valid CIDR block."
  }
}
```

### Pre/Post Conditions

```hcl
resource "aws_subnet" "private" {
  for_each                = var.private_subnets
  vpc_id                  = aws_vpc.this.id
  cidr_block              = each.value
  map_public_ip_on_launch = false

  lifecycle {
    precondition {
      condition     = tonumber(split("/", each.value)[1]) <= 24
      error_message = "Private subnet CIDR must be /24 or smaller (got ${each.value})."
    }
    postcondition {
      condition     = self.state == "available"
      error_message = "Subnet ${self.id} did not reach 'available' state after creation."
    }
  }
}
```

---

## State Management

### Remote State Configuration

```hcl
terraform {
  backend "s3" {
    bucket         = "my-terraform-state"
    key            = "vpc/terraform.tfstate"
    region         = "us-east-1"
    encrypt        = true
    dynamodb_table = "terraform-locks"
    kms_key_id     = "arn:aws:kms:us-east-1:123456789012:key/12345678-1234-1234-1234-123456789012"
  }
}
```

### State Operations

```bash
# Import existing resource
terraform import aws_vpc.main vpc-12345

# Move resource
terraform state mv aws_vpc.old aws_vpc.new

# Remove from state (doesn't destroy)
terraform state rm aws_instance.temp

# Refresh state
terraform apply -refresh-only
```

---

## Lifecycle & Dependencies

### Lifecycle Rules

```hcl
resource "aws_s3_bucket" "critical" {
  bucket = "${var.app}-${var.environment}-state"

  lifecycle {
    prevent_destroy = true
  }
}

resource "aws_launch_template" "app" {
  name_prefix   = "${var.app}-${var.environment}"
  image_id      = data.aws_ami.ubuntu.id
  instance_type = var.instance_type

  lifecycle {
    create_before_destroy = true
  }
}
```

### Dependencies

```hcl
# ❌ BAD: Unnecessary explicit dependency
resource "aws_subnet" "this" {
  vpc_id     = aws_vpc.this.id
  depends_on = [aws_vpc.this]  # Redundant!
}

# ✅ GOOD: Let Terraform infer from references
resource "aws_subnet" "this" {
  vpc_id = aws_vpc.this.id  # Dependency automatically inferred
}
```

---

## Security & Secrets

### Secret Management

```hcl
variable "db_password" {
  type        = string
  sensitive   = true
  description = "Database password from Secrets Manager."
}

output "admin_password" {
  value     = var.db_password
  sensitive = true
}
```

### IAM Best Practices

```hcl
data "aws_iam_policy_document" "lambda_policy" {
  statement {
    effect = "Allow"
    actions = [
      "logs:CreateLogGroup",
      "logs:CreateLogStream",
      "logs:PutLogEvents",
    ]
    resources = ["arn:aws:logs:${var.region}:${data.aws_caller_identity.current.account_id}:log-group:/aws/lambda/${var.function_name}:*"]
  }
}
```

---

## Common Mistakes & Anti-Patterns

### Using count with Maps

```hcl
# ❌ BAD: count with maps/lists (fragile addressing)
variable "subnets" {
  default = ["10.0.1.0/24", "10.0.2.0/24"]
}

resource "aws_subnet" "this" {
  count      = length(var.subnets)
  cidr_block = var.subnets[count.index]
  # Reordering var.subnets will destroy/recreate in wrong order!
}

# ✅ GOOD: for_each with map (stable addressing)
variable "subnets" {
  default = {
    "az-a" = "10.0.1.0/24"
    "az-b" = "10.0.2.0/24"
  }
}

resource "aws_subnet" "this" {
  for_each   = var.subnets
  cidr_block = each.value
}
```

### Hardcoded Credentials

```hcl
# ❌ BAD: Hardcoded secrets
resource "aws_db_instance" "this" {
  password = "MyPassword123!"  # NEVER DO THIS!
}

# ✅ GOOD: Use variable marked sensitive
variable "db_password" {
  type      = string
  sensitive = true
}

resource "aws_db_instance" "this" {
  password = var.db_password
}
```

### Missing Provider Versions

```hcl
# ❌ BAD: No version constraints
terraform {
  required_providers {
    aws = {
      source = "hashicorp/aws"
    }
  }
}

# ✅ GOOD: Pin to major version
terraform {
  required_version = ">= 1.12.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.0"  # Allow 6.x, but not 7.x
    }
  }
}
```

### Monolithic State Files

```hcl
# ❌ BAD: One giant state for entire infrastructure
# terraform/
#   main.tf  (contains VPC, EKS, RDS, Lambda, etc.)

# ✅ GOOD: Separate states by blast radius
# terraform/
#   networking/     (VPC, subnets - changes rarely)
#   eks/           (EKS cluster - moderate changes)
#   applications/  (Lambda, services - frequent changes)
```

---

## Performance Optimization

### Data Source Optimization

```hcl
# ❌ BAD: Repeated data source calls
resource "aws_instance" "web1" {
  ami = data.aws_ami.ubuntu.id
}
resource "aws_instance" "web2" {
  ami = data.aws_ami.ubuntu.id  # Same data source called again
}

# ✅ GOOD: Cache data source result
locals {
  ami_id = data.aws_ami.ubuntu.id
}

resource "aws_instance" "web1" {
  ami = local.ami_id
}
resource "aws_instance" "web2" {
  ami = local.ami_id
}
```

### Plan Optimization

```bash
# Save plan for consistency
terraform plan -out=tfplan

# Review plan
terraform show tfplan

# Apply saved plan (faster, consistent)
terraform apply tfplan

# Plan specific resources
terraform plan -target=module.vpc
```

---

## Troubleshooting

### Debug Logging

```bash
# Enable debug logging
export TF_LOG=DEBUG
export TF_LOG_PATH=terraform-debug.log
terraform apply

# Log levels: TRACE, DEBUG, INFO, WARN, ERROR
export TF_LOG=TRACE  # Most verbose
```

### State Lock Issues

```bash
# Error: Error acquiring the state lock
# Solution: Check for stuck locks
aws dynamodb scan --table-name terraform-locks

# Force unlock (use with caution)
terraform force-unlock <LOCK_ID>
```

### Resource Already Exists

```bash
# Error: resource already exists
# Solution: Import existing resource
terraform import aws_vpc.this vpc-0abc1234

# Or use import blocks (Terraform 1.5+)
import {
  to = aws_vpc.this
  id = "vpc-0abc1234"
}
```

### Drift Detection

```bash
# Refresh state from real infrastructure
terraform apply -refresh-only

# Show what changed
terraform plan -refresh-only
```

---

## Import Strategies

### Terraform 1.5+ Import Blocks (Preferred)

```hcl
# Import existing VPC into Terraform management
import {
  to = aws_vpc.this
  id = "vpc-0abc1234def56789"
}

resource "aws_vpc" "this" {
  cidr_block = "10.0.0.0/16"
  # ... rest of configuration
}
```

### Legacy Import Command

```bash
# Pre-1.5 method (still works)
terraform import aws_vpc.this vpc-0abc1234def56789

# Import into module
terraform import module.vpc.aws_vpc.this vpc-0abc1234def56789

# Import with for_each
terraform import 'aws_subnet.private["az-a"]' subnet-0abc1234
terraform import 'aws_subnet.private["az-b"]' subnet-5678def9
```

---

## Workspaces

### When to Use Workspaces

- **✅ GOOD**: Multiple environments (dev/staging/prod) with identical infrastructure topology
- **❌ BAD**: Completely different architectures per environment (use separate state files instead)

### Workspace Commands

```bash
terraform workspace list           # List workspaces
terraform workspace new dev        # Create workspace
terraform workspace select dev     # Switch workspace
terraform workspace show           # Show current workspace
terraform workspace delete staging # Delete workspace
```

### Workspace-Aware Configuration

```hcl
locals {
  environment = terraform.workspace

  # Workspace-specific sizing
  instance_counts = {
    dev     = 1
    staging = 2
    prod    = 5
  }

  instance_count = local.instance_counts[local.environment]
}
```

---

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Terraform

on:
  pull_request:
    branches: [main]
    paths:
      - 'terraform/**'
  push:
    branches: [main]

permissions:
  contents: read
  pull-requests: write
  id-token: write  # For OIDC

jobs:
  terraform:
    name: Terraform Plan/Apply
    runs-on: ubuntu-latest

    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Configure AWS Credentials
        uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: arn:aws:iam::123456789012:role/GitHubActionsRole
          aws-region: us-east-1

      - name: Setup Terraform
        uses: hashicorp/setup-terraform@v3
        with:
          terraform_version: 1.6.0

      - name: Terraform Format Check
        run: terraform fmt -check -recursive

      - name: Terraform Init
        run: terraform init

      - name: Terraform Validate
        run: terraform validate

      - name: Run TFLint
        uses: terraform-linters/setup-tflint@v4

      - name: Terraform Plan
        run: |
          terraform plan -out=tfplan -no-color
          terraform show -no-color tfplan > plan.txt

      - name: Terraform Apply
        if: github.ref == 'refs/heads/main' && github.event_name == 'push'
        run: terraform apply -auto-approve tfplan
```

### Best Practices for CI/CD

- **Use OIDC** instead of long-lived credentials
- **Save plan files** (`-out=tfplan`) and apply them for consistency
- **Comment plans** on pull requests for review
- **Run security scans** (Checkov, tfsec) before apply
- **Lock Terraform version** in CI to match local development

---

## Move/Rename Strategies

### Renaming Resources

```bash
# Rename resource in state without destroying
terraform state mv aws_instance.old_name aws_instance.new_name

# Move resource into module
terraform state mv aws_vpc.this module.networking.aws_vpc.this

# Rename for_each key
terraform state mv 'aws_subnet.private["old-key"]' 'aws_subnet.private["new-key"]'
```

### Refactoring with moved Block (Terraform ≥1.1)

```hcl
# Old configuration
resource "aws_instance" "web" {
  # ...
}

# New configuration with moved block
moved {
  from = aws_instance.web
  to   = aws_instance.app
}

resource "aws_instance" "app" {
  # Same config, new name
}
```

---

## Provider Configuration

### AWS Provider Hygiene

```hcl
provider "aws" {
  region = var.region

  default_tags {
    tags = {
      app         = var.app
      environment = var.environment
      owner       = var.owner
      managed_by  = "terraform"
    }
  }
}

provider "aws" {
  alias  = "eu"
  region = "eu-central-1"
}
```

---

## Review Checklist

When reviewing Terraform code, check:

- [ ] Provider versions pinned (`~> 6.0`)
- [ ] Variables have validations
- [ ] Sensitive data marked as `sensitive = true`
- [ ] Remote state configured with locking
- [ ] `for_each` used instead of `count` for stability
- [ ] Lifecycle rules for critical resources
- [ ] Tags applied consistently
- [ ] No hardcoded secrets or credentials
- [ ] Module structure follows conventions
- [ ] Documentation present (README.md)
- [ ] Pre/post conditions for critical validations
