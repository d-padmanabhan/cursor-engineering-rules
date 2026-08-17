# Multi-Tenant Report Worker

All tenants submit report jobs to one unbounded queue. Workers fetch jobs in arrival order and start an unbounded coroutine for each message.

One enterprise tenant can submit 500,000 reports during month-end. Small tenants normally submit fewer than 100. The API always returns `202 Accepted`; it does not expose queue age, a completion deadline, cancellation, or rejection.

Workers retry every exception five times. There are no per-tenant quotas, priority classes, concurrency limits, queue-age limits, memory bounds, load shedding, or backlog-recovery plan. The dashboard reports worker CPU and total queue depth only.
