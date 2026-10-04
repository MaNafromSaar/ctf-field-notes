# Using a supplied Kubernetes client configuration

## Observation

The challenge supplied a Kubernetes client configuration and a remote API endpoint. The configuration contained client authentication material. The API server certificate did not match the public challenge name, so the local trust setup needed investigation before API calls could work.

## Connect and inspect

Work on a copy of the supplied configuration and replace only the server endpoint with the current authorized instance value. Keep the original file unchanged and private. If certificate verification prevents a challenge connection, understand the trust mismatch before choosing a temporary verification override; do not carry that insecure setting into real clusters.

Use `kubectl` to inspect the active context and namespaces, then enumerate the resource type relevant to the task. Kubernetes Secret data is Base64-encoded by default; Base64 is an encoding, not encryption. Do not publish the supplied client key, token, kubeconfig, or decoded secret.

## Takeaway

Treat a kubeconfig as a credential, not as harmless configuration. Separate endpoint discovery, TLS validation, authentication, and authorization so that an error at one layer does not lead to blind changes at another.
