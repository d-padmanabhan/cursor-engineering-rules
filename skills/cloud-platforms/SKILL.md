---
name: cloud-platforms
description: Cloud platform best practices for AWS, Azure, GCP, and Cloudflare. Covers Zero Trust architecture, IAM patterns, EKS/AKS/GKE configurations, serverless patterns, and multi-cloud strategies. Use when working with cloud infrastructure, AWS services, Azure resources, GCP projects, Cloudflare Workers, or when asking about cloud architecture and deployment.
---

# Cloud Platforms

## Core Principles

1. **Zero Trust**: Never trust, always verify
2. **Least Privilege**: Minimum necessary permissions
3. **Defense in Depth**: Multiple layers of security
4. **Infrastructure as Code**: All infrastructure defined in code
5. **Observability**: Comprehensive logging, metrics, and tracing

## Platform Selection

| Use Case | Recommended |
|----------|-------------|
| Enterprise, broad services | AWS |
| Microsoft ecosystem | Azure |
| Data/ML workloads | GCP |
| Edge/CDN, simple serverless | Cloudflare |

## AWS Quick Reference

### IAM Best Practices

```hcl
# EKS Pod Identity (Recommended over IRSA)
resource "aws_eks_pod_identity_association" "app" {
  cluster_name    = aws_eks_cluster.main.name
  namespace       = "default"
  service_account = "app"
  role_arn        = aws_iam_role.app_pod_identity.arn
}
```

### VPC Pattern

```hcl
# Private subnets only - Zero Trust
resource "aws_subnet" "private" {
  count             = 3
  vpc_id            = aws_vpc.main.id
  cidr_block        = "10.16.${count.index + 1}.0/24"
  availability_zone = data.aws_availability_zones.available.names[count.index]

  tags = {
    Name = "private-subnet-${count.index + 1}"
    Type = "Private"
  }
}
```

### Essential Services

- **EKS**: Managed Kubernetes
- **Lambda**: Serverless compute
- **RDS/Aurora**: Managed databases
- **S3**: Object storage
- **CloudFront**: CDN
- **Secrets Manager**: Secret storage

## Azure Quick Reference

### Managed Identity

```hcl
resource "azurerm_user_assigned_identity" "app" {
  name                = "app-identity"
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
}
```

### Essential Services

- **AKS**: Managed Kubernetes
- **Azure Functions**: Serverless
- **Azure SQL**: Managed databases
- **Blob Storage**: Object storage
- **Azure CDN**: Content delivery
- **Key Vault**: Secret management

## GCP Quick Reference

### Workload Identity

```hcl
resource "google_service_account" "app" {
  account_id   = "app-sa"
  display_name = "Application Service Account"
}

resource "google_project_iam_member" "app" {
  project = var.project_id
  role    = "roles/storage.objectViewer"
  member  = "serviceAccount:${google_service_account.app.email}"
}
```

### Essential Services

- **GKE**: Managed Kubernetes
- **Cloud Functions**: Serverless
- **Cloud SQL**: Managed databases
- **Cloud Storage**: Object storage
- **Cloud CDN**: Content delivery
- **Secret Manager**: Secrets

## Cloudflare Quick Reference

### Workers

```javascript
export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    
    if (url.pathname === '/api/data') {
      const data = await env.MY_KV.get('key');
      return new Response(JSON.stringify({ data }), {
        headers: { 'Content-Type': 'application/json' }
      });
    }
    
    return new Response('Hello World');
  }
};
```

### Essential Services

- **Workers**: Edge compute
- **Pages**: Static site hosting
- **D1**: SQLite database
- **KV**: Key-value storage
- **R2**: S3-compatible storage

## Security Checklist

- [ ] IAM roles with least privilege
- [ ] Network segmentation (VPCs, security groups)
- [ ] Encryption at rest and in transit
- [ ] Secret management (not in code)
- [ ] Audit logging enabled
- [ ] Multi-factor authentication
- [ ] Regular security assessments

## Detailed References

- **AWS**: See [references/aws.md](references/aws.md) for EKS, IAM, networking
- **Azure**: See [references/azure.md](references/azure.md) for AKS, identity
- **GCP**: See [references/gcp.md](references/gcp.md) for GKE, IAM
- **Cloudflare**: See [references/cloudflare.md](references/cloudflare.md) for Workers, Pages
- **Identity protocols**: See [../security-testing/references/identity-access.md](../security-testing/references/identity-access.md) for OIDC/PKCE and SAML/ADFS validation
