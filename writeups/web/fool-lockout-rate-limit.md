# Fool Lockout: a rate-limit window mistaken for a lockout

## Context

The challenge provides a login application, its source, and a credential list. The goal is to test those credentials against the assigned instance. The supplied source and credential list are intentionally omitted from this portfolio.

## Observations

The login handler accepts both `GET` and `POST`, but only `POST` processes username and password fields. The rate-limit function increments its per-IP counter on `POST`; the login route checks this counter before authenticating. With a threshold of ten, the eleventh POST in the current window receives the rate-limit response.

## Hypothesis

The nominal 120-second lockout may not be enforced if the request counter is reset after the shorter 30-second epoch. Inspecting the check path can disprove this: if every request checks `lockout_until` before continuing, waiting for the epoch alone will not help.

## Analysis

The source does set `lockout_until` after the threshold is exceeded, but the request path never checks that timestamp to decide whether to reject a request. Instead, refreshing the per-IP state resets `num_requests` once more than 30 seconds have elapsed since the epoch began. Therefore the effective limit is ten POSTs per 30-second window, not a 120-second block.

Changing a login request from POST to GET is not a useful bypass: GET does not submit credentials, and the login handler only authenticates inside its POST branch. The practical approach is to submit at most ten credential pairs, wait 31 seconds, and continue. The helper uses a `requests.Session`, sends form-encoded POSTs, disables automatic redirect following, and treats the login redirect as success. The redirect is distinct from the normal 200 response for invalid credentials.

Run it only against the authorized challenge instance, supplying the instance URL and the locally held credential file:

```sh
python scripts/fool_lockout_credential_tester.py 'http://<HOST>:<PORT>' --credentials "$CREDENTIAL_FILE"
```

The helper pauses at each ten-attempt boundary and also recovers if it receives the rate-limit response unexpectedly. `--show-match` opts into printing the matching credential locally. The script does not follow the success redirect or print the flag.

## Takeaways

An IP-based limiter is only as strong as the state transition actually enforced. Keep the lockout check explicit, define whether the window is fixed or sliding, and test boundary requests. Changing HTTP methods only matters when the application accepts those methods for the same operation.

## Artifacts intentionally omitted

The challenge source bundle and supplied username-password list are not included.