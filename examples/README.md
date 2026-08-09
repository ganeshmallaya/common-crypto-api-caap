# Examples

These files exercise the implemented research slice. Identifiers and payloads
are non-production examples. Start the service, then run `quickstart.sh`.

The script requires `curl`, Python 3, and a local service at
`http://127.0.0.1:8080`. It creates an ephemeral key, signs a message, and
verifies the signature. The key disappears when the service stops.
