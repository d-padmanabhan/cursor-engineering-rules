# Templates: Terraform (`cloudflare_ruleset`)

Drop-in HCL templates for both rule types. Pair with `405-cloudflare-waf-rules.mdc` § "Provenance without comment slop" and the cumulative anti-patterns list.

**Conventions:**

- `$trusted_egress_ips` is a placeholder for your zone's named [IP List](https://developers.cloudflare.com/waf/tools/lists/). Replace with the actual list name configured in your account.
- `<your-app>`, `<host>`, `<endpoint>`, and `<ticket-id>` are placeholders - replace before applying.
- All multi-value headers use the `any(... [*] ...)` form. Bare `eq` against a header is wrong.
- Country codes pasted from the [Cloudflare country code reference](https://developers.cloudflare.com/network/country-codes/), never typed.
- Remove all template-only comments after filling the rule.

---

## Custom Rule (phase `http_request_firewall_custom`)

The most common case is an allow + block pair. Draft both rules and confirm the **allow is positioned ABOVE the block** in the file (Cloudflare evaluates top-down; first match wins).

```hcl
# <YYYY-MM-DD> / <ticket-id> - <host or rule purpose> added to <allowed or blocked scope>.
# <Optional: unusual source scope, accepted risk, known gap, or expiry.>

# Allow trusted IPs + sanctioned regions (skip-as-allow). Positioned ABOVE the block rule.
{
  action      = "skip"
  description = "<your-app>-allow-<region-or-purpose>"
  enabled     = true
  expression  = <<-EOT
    http.host eq "<host>"
    and (ip.geoip.country in {"US" "CA" "GB"} or ip.src in $trusted_egress_ips)
  EOT
  logging = {
    enabled = true
  }
  action_parameters = {
    ruleset = "current"
  }
},

# Block everything else for this host. Positioned BELOW the allow.
{
  action      = "block"
  description = "<your-app>-block-non-allowlisted"
  enabled     = true
  expression  = <<-EOT
    http.host eq "<host>"
  EOT
  logging = {
    enabled = true
  }
},
```

> [!CAUTION]
> Before promoting `block` to enforced state, run it as `action = "log"` for at least 24h and confirm via Security Events that ONLY illegitimate traffic matches. The most common production incident is a block rule that matches legitimate traffic because the predicate was broader than the requester realized.

---

## Managed-Rule Exception (phase `http_request_firewall_managed`, action `skip`)

```hcl
# <YYYY-MM-DD> / <ticket-id> - <host and endpoint> added to the managed-rule exception.
# <Optional: Ray ID, child-rule lineage/addition, unusual source scope, known gap, or expiry.>
{
  action      = "skip"
  description = "<your-app>-<endpoint>-skip"
  enabled     = true
  expression  = <<-EOT
    <host predicate>             # http.host eq "..." | http.host in {"..." "..."}
    and http.request.method eq "<METHOD>"
    and <path predicate>          # see decision matrix in 405-cloudflare-waf-rules.mdc
    and <content-type guard>      # any(lower(http.request.headers["content-type"][*])[*] contains "multipart/form-data")
    and <body marker>             # http.request.body.raw contains "filename="  (multipart only)
    and <origin guard>            # any(http.request.headers["origin"][*] eq "https://<browser-host>")  (browser flow only)
    and <source guard>            # ip.src in $trusted_egress_ips  (and/or ip.geoip.continent in {...})
  EOT
  action_parameters = {
    rules = {
      (local.waf_ruleset_ids.cloudflare_owasp_core_ruleset_id) = [
        "<owasp-rule-id-1>",
        "<owasp-rule-id-2>",
      ]
    }
  }
},
```

> [!IMPORTANT]
> The OWASP child-rule IDs above are placeholders. The actual IDs change per Cloudflare ruleset version and per zone. Always source them from Security Events on the consuming zone. Hardcoding a baseline from another zone's history is how you ship overscoped skip rules.

---

## Notes on `logging.enabled`

- **`block` and `challenge` actions:** enable logging. Without it, blocked / challenged traffic is harder to see in Security Events.
- **`skip` action (custom rule used as allow):** enable logging. The allow is a policy decision worth recording for debugging.
- **`skip` action (managed-rule exception):** logging block can be omitted. Cloudflare records skip-rule matches in WAF events automatically; the `logging` block is for *additional* logging beyond the default. The original template carried `logging.enabled = true` everywhere as a defensive copy-paste - it's harmless but not required for skip exceptions.

---

## Pre-flight: Terraform validation

Before opening the PR:

```bash
terraform fmt -recursive
terraform validate
terraform plan -out=plan.tfplan
# Eyeball the plan diff - it should be exactly your new / modified rule(s) and nothing else.
```

If the plan shows changes you didn't make, **stop** - someone has been editing via the Dashboard / API and the source-of-truth is broken. Investigate before applying.
