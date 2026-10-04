# A bounded rate-limit failover condition

## Model the request path

The challenge used a primary web service behind a proxy and a backup service. Source inspection showed that requests shared one global rate-limit bucket, the primary translated rate-limit rejection into an HTTP error used by the proxy's health check, and the backup was enabled when the primary was marked unhealthy.

The important chain was:

```text
shared request budget exhausted
  -> primary health-check response fails
  -> proxy marks primary unavailable
  -> configured backup receives traffic
```

## Verify rather than assume

Read the limiter key function, the handler for rejected requests, and the proxy's health-check and backup configuration. These components must agree for failover to occur. A per-client limiter, a health check that bypasses application limits, or a different error mapping would change the result.

In the challenge environment, the helper used a finite request burst and waited for the configured health-check transitions. Keep any reproduction bounded and restricted to the assigned instance; this is an availability test, not a technique for arbitrary services.

## Defensive lessons

Do not make health-check availability depend on an unrelated user request budget. Use a dedicated health endpoint, isolate its limiter behavior, and make failover thresholds explicit. A global limiter can create cross-client denial of service even when each client's behavior is modest.
