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
