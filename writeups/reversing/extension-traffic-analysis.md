# Extension traffic analysis: distinguish intent from execution

## Trace the event path

The extension registers a `webNavigation.onCompleted` listener. On each completed navigation, the background handler logs the visited URL, builds a JSON payload containing that URL, and issues a POST request. This is a broad collection trigger: it is attached to navigation completion rather than an explicit user action in the popup.

## Inspect the encrypted destination

The source contains a URL-safe Base64 key with the length expected by Fernet and a Fernet-looking token assigned to the request destination. Treat both as data and inspect them offline with [`scripts/decrypt_fernet.py`](../../scripts/decrypt_fernet.py). Do not automatically contact a recovered address.

There is an important implementation mismatch: the shown handler declares the key but never calls Fernet decryption. It passes the token string directly to `fetch` as the URL. Thus the encrypted value may reveal the intended destination during analysis, but the displayed code does not itself decrypt that value before sending the request.

## Takeaway

Permission scope, event registration, payload construction, and the actual network call together establish behavior. Separate what the author appears to intend from what the code executes; unused key material is a clue, not proof of a working decryption path.
