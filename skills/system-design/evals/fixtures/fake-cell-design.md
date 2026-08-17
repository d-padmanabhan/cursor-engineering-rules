# Proposed Cellular Order Platform

The platform will deploy eight identical application stacks called cells. A global gateway looks up `tenant_id` in a routing table and forwards each request to one cell.

All cells:

- read and write the same global orders database;
- publish to the same queue;
- fetch routing and feature configuration synchronously for every request from one control-plane service;
- share one cloud account and its service quotas;
- deploy simultaneously from one pipeline;
- retry another cell when the assigned cell returns an error.

The proposal claims any cell can fail without affecting another. Cell capacity, tenant placement, migration, routing-map versioning, overload behavior, data authority, and evacuation have not been defined.
