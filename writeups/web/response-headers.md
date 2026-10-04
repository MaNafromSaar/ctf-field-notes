# Inspecting response headers across HTTP methods

## Observation

The visible page suggested two states associated with common request methods. A third state appeared when trying another method, but its HTML body contained no useful value. That was a cue to inspect the full HTTP response rather than infer from the rendered page alone.

## Investigation

Use an authorized challenge URL and compare the status, body, and headers for the supported methods. `curl -i -X <METHOD> <URL>` displays response headers alongside the body. Browser developer tools' Network panel are another option; select the request and inspect the complete response-header list.

A custom response header can carry application data even when the body appears intentionally uninformative. Check whether a proxy or client UI is hiding headers before concluding that the server returned nothing.

## Takeaway

HTTP responses have more than a body. Method-dependent branches and custom headers are worth checking when visible page content does not explain the observed state.
