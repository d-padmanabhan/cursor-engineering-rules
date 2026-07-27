# Synthetic current-state fixture for the Cloudflare WAF author eval suite.

resource "cloudflare_ruleset" "managed_waf" {
  zone_id     = var.zone_id
  name        = "Managed WAF"
  description = "Managed WAF execution and narrow exceptions"
  kind        = "zone"
  phase       = "http_request_firewall_managed"

  rules {
    action      = "skip"
    description = "Permit known health-check false positive"
    expression  = "(http.host eq \"status.acme.com\" and http.request.uri.path eq \"/health\" and http.request.method eq \"GET\")"

    action_parameters {
      rules = {
        "efb7b8c949ac4650a09736fc376e9aee" = [
          "f1a0a7e20f2749e2a4b8f9488d224dd3"
        ]
      }
    }
  }

  rules {
    action      = "execute"
    description = "Execute Cloudflare OWASP managed ruleset"
    expression  = "true"

    action_parameters {
      id = "efb7b8c949ac4650a09736fc376e9aee"
    }
  }
}
