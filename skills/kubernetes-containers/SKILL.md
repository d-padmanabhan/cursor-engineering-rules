---
name: kubernetes-containers
description: Kubernetes and Helm best practices for container orchestration. Covers deployments, services, RBAC, resource management, Helm charts, and production patterns. Use when working with Kubernetes manifests, Helm charts, kubectl commands, or when asking about container orchestration, pod configuration, or cluster management.
---

# Kubernetes & Containers

## Core Concepts

- **Pods**: Smallest deployable units
- **Deployments**: Declarative pod management
- **Services**: Network abstraction
- **ConfigMaps/Secrets**: Configuration injection
- **RBAC**: Access control

## Essential Commands

```bash
# Context & Namespace
kubectl config get-contexts
kubectl config use-context prod
kubectl get pods -n my-namespace

# Pod Operations
kubectl get pods -o wide
kubectl describe pod <pod-name>
kubectl logs <pod-name> -f --tail=100
kubectl exec -it <pod-name> -- /bin/sh

# Apply & Delete
kubectl apply -f manifest.yaml
kubectl delete -f manifest.yaml
kubectl rollout restart deployment/<name>

# Kustomize
kubectl kustomize overlays/dev
kubectl diff -k overlays/dev
kubectl apply -k overlays/dev

# Debugging
kubectl get events --sort-by='.lastTimestamp'
kubectl top pods
kubectl port-forward svc/my-service 8080:80
```

## Deployment Pattern

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: app
  labels:
    app: my-app
spec:
  replicas: 3
  selector:
    matchLabels:
      app: my-app
  template:
    metadata:
      labels:
        app: my-app
    spec:
      serviceAccountName: app-sa
      securityContext:
        runAsNonRoot: true
        runAsUser: 1000
        fsGroup: 1000
      containers:
        - name: app
          image: myapp:1.0.0
          ports:
            - containerPort: 8080
          resources:
            requests:
              cpu: 100m
              memory: 128Mi
            limits:
              cpu: 500m
              memory: 512Mi
          livenessProbe:
            httpGet:
              path: /health
              port: 8080
            initialDelaySeconds: 10
            periodSeconds: 10
          readinessProbe:
            httpGet:
              path: /ready
              port: 8080
            initialDelaySeconds: 5
            periodSeconds: 5
          securityContext:
            allowPrivilegeEscalation: false
            readOnlyRootFilesystem: true
```

## Readiness and Liveness Probes

Readiness and liveness probes are health checks used by Kubernetes to manage the lifecycle and traffic flow of your containers.

- **Liveness Probe**: Determines if a container is still running correctly. If it fails, Kubernetes kills the container and starts a new one based on the restart policy
- **Readiness Probe**: Determines if a container is ready to start accepting network traffic. If it fails, the Pod's IP address is removed from the Endpoints of all Services, ensuring no requests are sent to an unready application

### Key Implementation Methods

Both probes can be configured using three main mechanisms:

- **HTTP GET**: Kubernetes sends an HTTP request to a specific endpoint (for example `/healthz`). A status code between 200-399 indicates success
- **TCP Socket**: Kubernetes attempts to open a TCP connection to a specified port. If the connection is established, the probe is successful
- **Exec Action**: Kubernetes executes a command inside the container. If the command returns an exit code of 0, the probe is successful

## EKS Traffic Routing (ALB/NLB and VPC Lattice - Pod IP Targets)

On EKS, AWS controllers can route to workloads using either **node targets** or **pod IP targets**.

### AWS Load Balancer Controller (ALB/NLB)

- **Instance targets**: register worker nodes in the AWS target group. Traffic reaches a node (often via NodePort) and is forwarded to a pod by kube-proxy
- **IP targets**: register pod IPs in the AWS target group. Traffic routes directly to pods, avoiding the NodePort + kube-proxy hop

Common configuration knobs:

- **ALB Ingress**: `alb.ingress.kubernetes.io/target-type: ip` (or `instance`)
- **NLB Service**: `service.beta.kubernetes.io/aws-load-balancer-nlb-target-type: "ip"`

### Amazon VPC Lattice Gateway API Controller

When using VPC Lattice with Kubernetes (Gateway API), the controller can register **pod IPs** into VPC Lattice target groups and route requests directly to pods.

- **Pod registration**: pod IPs are registered as targets (no node-level hop)
- **Readiness gates**: pods can be gated on successful registration and target health to reduce rollout 5XX

## Service Pattern

```yaml
apiVersion: v1
kind: Service
metadata:
  name: app
spec:
  type: ClusterIP
  selector:
    app: my-app
  ports:
    - port: 80
      targetPort: 8080
```

## Resource Management

| Resource | Request | Limit |
|----------|---------|-------|
| CPU | Guaranteed minimum | Throttled above |
| Memory | Guaranteed minimum | OOMKilled above |

Always set both requests and limits:

```yaml
resources:
  requests:
    cpu: 100m      # 0.1 CPU
    memory: 128Mi
  limits:
    cpu: 500m      # 0.5 CPU
    memory: 512Mi
```

## Security Best Practices

```yaml
# Pod Security Context
securityContext:
  runAsNonRoot: true
  runAsUser: 1000
  fsGroup: 1000

# Container Security Context
securityContext:
  allowPrivilegeEscalation: false
  readOnlyRootFilesystem: true
  capabilities:
    drop:
      - ALL
```

## Helm Quick Reference

```bash
# Install/Upgrade
helm install my-app ./chart
helm upgrade my-app ./chart
helm upgrade --install my-app ./chart

# Values
helm install my-app ./chart -f values-prod.yaml
helm install my-app ./chart --set image.tag=1.0.0

# Debug
helm template my-app ./chart
helm lint ./chart
helm diff upgrade my-app ./chart
```

## Detailed References

- **Kubernetes Patterns**: See [references/kubernetes-patterns.md](references/kubernetes-patterns.md)
- **Helm Charts**: See [references/helm-charts.md](references/helm-charts.md)
