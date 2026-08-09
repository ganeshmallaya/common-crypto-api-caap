# Examples

These files exercise the implemented research slice. Identifiers and payloads
are non-production examples. Start the service, then run `quickstart.sh`.

The script requires `curl`, Python 3 and a local service at
`http://127.0.0.1:8080`. It creates an ephemeral key, signs a message and
verifies the signature. The key disappears when the service stops.

## Version 2 algorithm examples

The executable slice remains Ed25519 while the v2 research profile in
`api/profiles/pqc-signing-v2.profile.json` specifies RSA-PSS with SHA-256,
ECDSA P-256 with SHA-256 and ML-DSA-65. These entries are `specified`, not
`implemented`; provider execution and test vectors are still required.

## ECDSA P-256 to ML-DSA-65

An algorithm transformation creates a new ML-DSA key; it does not convert the
ECC private key. Inventory signers and verifiers, create an opaque ML-DSA key,
distribute verification material, activate a bounded overlap profile, disable
ECDSA signing and finally retire the ECC key under lifecycle policy. At no
stage does ML-DSA failure authorize ECDSA fallback.
