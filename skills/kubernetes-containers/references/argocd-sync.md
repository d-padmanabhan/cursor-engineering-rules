# Argo CD Synchronization

Use this workflow to preview, authorize, execute, verify, and recover an Argo CD synchronization without bypassing Git as the declared source of truth.

> [!IMPORTANT]
> `argocd app sync`, `argocd app rollback`, and sync-window overrides mutate remote state. Read-only inspection does not authorize a later mutation.

## Preconditions

- Use a least-privilege Argo CD identity and a verified CLI context.
- Know the Application name, AppProject, destination cluster and namespace, repository, and intended commit SHA.
- Confirm the revision exists in the configured source. Do not present a moving branch name as the production approval target.
- Identify the change request, approver, maintenance window, expected health checks, and recovery commit before syncing.
- For multi-source Applications, identify each source by name or position and pin every revision involved.

## Read-Only Preflight

Set explicit values and preserve the outputs with the change record:

```bash
APP="payments-production"
REVISION="0123456789abcdef0123456789abcdef01234567"
TIMEOUT_SECONDS="600"

argocd app get "${APP}" --refresh --output json >"${APP}-before.json"
argocd app diff "${APP}" --revision "${REVISION}" --refresh
argocd app sync "${APP}" --revision "${REVISION}" --dry-run --prune
```

`argocd app diff` returns `1` when it finds a diff, `0` when there is no diff, and `2` for a general error. Automation must distinguish "changes found" from an operational failure. Argo CD excludes Kubernetes Secret contents from this diff; verify secret references and external secret delivery separately.

The dry-run includes `--prune` so reviewers can see resources that would be deleted. It does not approve pruning. Before proceeding, inspect:

- Application metadata: `spec.project`, source repository/path/chart, destination server/name, and namespace
- all creates, updates, immutable-field replacements, and deletions
- cluster-scoped resources, CRDs, Namespaces, PVCs, finalizers, and resources with retention requirements
- resources tracked by another Application
- PreSync, Sync, PostSync, SyncFail, PreDelete, and PostDelete hooks
- negative and positive sync waves, dependency ordering, and hook deletion policies
- active sync windows and whether a manual override is being requested

Stop if the identity, destination, revision, generated manifests, prune set, ownership, or recovery path is uncertain.

## Production Approval Gate

The approver must see:

- Application and AppProject
- destination cluster and namespace
- exact commit SHA for every source
- diff and dry-run artifacts
- explicit prune list
- hooks, waves, sync options, and sync-window status
- expected completion and health signals
- recovery commit or revert procedure

Approval is scoped to this target and revision. A changed revision, destination, prune set, or use of `--force`, `--replace`, or a sync-window override requires new approval.

## Manual Synchronization

When no pruning is required:

```bash
argocd app sync "${APP}" \
  --revision "${REVISION}" \
  --timeout "${TIMEOUT_SECONDS}" \
  --info "change-request=CHG-1234"

argocd app wait "${APP}" \
  --operation \
  --sync \
  --health \
  --timeout "${TIMEOUT_SECONDS}"
```

When the reviewed prune set is explicitly approved, add `--prune`:

```bash
argocd app sync "${APP}" \
  --revision "${REVISION}" \
  --prune \
  --timeout "${TIMEOUT_SECONDS}" \
  --info "change-request=CHG-1234"

argocd app wait "${APP}" \
  --operation \
  --sync \
  --health \
  --timeout "${TIMEOUT_SECONDS}"
```

Do not use `--force` as a retry mechanism. It enables force apply and can replace resources in ways that cause outages or data loss. Selective resource sync is also not a normal recovery tool because it can bypass hooks and leave the Application only partially reconciled.

Success requires all of the following:

- the operation completed successfully;
- synchronization status is `Synced`;
- health status is `Healthy`;
- hooks completed as expected;
- application-level smoke checks and alerts are healthy;
- the deployed revision and operation evidence were recorded.

## Automated Synchronization Decisions

Set every automated-sync control explicitly:

```yaml
spec:
  syncPolicy:
    automated:
      enabled: true
      prune: false
      selfHeal: false
      allowEmpty: false
    syncOptions:
      - FailOnSharedResource=true
```

Review each control independently:

- `enabled`: Enable only after the repository controls, AppProject boundaries, destination, notifications, recovery process, and sync windows are ready.
- `prune`: Enable only when resource ownership and deletion behavior are understood. Keep it independent from `selfHeal`.
- `selfHeal`: Enable only when Git must overwrite live drift automatically, including emergency edits. Document the break-glass process.
- `allowEmpty`: Keep `false`. Set it to `true` only for a reviewed teardown workflow that may intentionally remove every managed resource.
- `FailOnSharedResource=true`: Prefer failing over silently taking ownership from another Application.
- `PruneLast=true`: Use when automated pruning is enabled unless a documented dependency requires another deletion order.
- `ServerSideApply=true`: Use only after reviewing field ownership, conflicts, admission behavior, and compatibility.
- `Replace=true` or `Force=true`: Treat as destructive exceptions requiring workload-specific review; never use them as universal defaults.
- hooks and waves: Keep hooks idempotent, observable, time-bounded, and safe to rerun. Test dependency and failure ordering.
- sync windows: Apply production allow/deny windows and tightly control manual overrides. A window is not a substitute for authorization or policy review.

For ApplicationSet-managed Applications, change the ApplicationSet or its source rather than patching the generated Application and assuming that change will persist.

## Failure Handling and Recovery

Do not immediately rerun a failed or degraded sync. Preserve evidence first:

```bash
argocd app get "${APP}" --show-operation --output yaml >"${APP}-failed-operation.yaml"
argocd app get "${APP}" --output tree=detailed >"${APP}-failed-tree.txt"
argocd app history "${APP}" >"${APP}-history.txt"
```

Then:

1. Identify the failed resource, hook, health assessment, ordering issue, admission rejection, or immutable-field conflict.
2. Stop automated retries if they are causing repeated side effects.
3. Revert or fix the bad Git commit through normal review.
4. Preview the resulting revision again, obtain authorization, sync it, and wait for `Synced` and `Healthy`.
5. Record the incident, revision transition, failed resources, recovery result, and any follow-up control change.

An emergency `argocd app rollback` is a break-glass mutation, not the default GitOps recovery path. If used, record the history ID and approval, then immediately reconcile Git so the next controller refresh does not reintroduce the bad state. Avoid unrecorded `kubectl apply`, parameter overrides, or live patches that hide drift from Git.

## References

- [Automated sync policy](https://argo-cd.readthedocs.io/en/release-3.4/user-guide/auto_sync/)
- [`argocd app diff`](https://argo-cd.readthedocs.io/en/release-3.4/user-guide/commands/argocd_app_diff/)
- [`argocd app sync`](https://argo-cd.readthedocs.io/en/release-3.4/user-guide/commands/argocd_app_sync/)
- [`argocd app wait`](https://argo-cd.readthedocs.io/en/release-3.4/user-guide/commands/argocd_app_wait/)
- [Sync options](https://argo-cd.readthedocs.io/en/release-3.4/user-guide/sync-options/)
- [Sync phases and waves](https://argo-cd.readthedocs.io/en/release-3.4/user-guide/sync-waves/)
- [Sync windows](https://argo-cd.readthedocs.io/en/release-3.4/user-guide/sync_windows/)
