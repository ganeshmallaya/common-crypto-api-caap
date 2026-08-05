# Before and After

**One migration, in code: access token signing from ES256 to a hybrid signature**

---

## 1. The scenario

An identity provider issues OAuth access tokens as signed JWTs. Six services issue them. Four groups of relying parties verify them. The current algorithm is `ES256`, which is ECDSA over P-256 with SHA-256.

A security policy now requires a hybrid signature. The target is ECDSA P-256 combined with ML-DSA-65. The classical half keeps a FIPS-validated hardware path. The post-quantum half defends the token against a future attack.

A repository search finds 66 places that name the algorithm.

![Before and after](images/04-before-after-whiteboard.svg)

---

## 2. Before: the algorithm lives in the call

Here is the pattern, in Java:

```java
// TokenIssuer.java  —  and 65 other places
private static final SignatureAlgorithm ALG = SignatureAlgorithm.ES256;

public String issueAccessToken(Subject subject, Set<String> scopes) {
    return Jwts.builder()
        .setSubject(subject.id())
        .claim("scope", String.join(" ", scopes))
        .setExpiration(Date.from(now().plus(TOKEN_TTL)))
        .signWith(this.signingKey, ALG)      // <-- the algorithm decision
        .compact();
}
```

One line carries six decisions.

1. The curve is P-256.
2. The hash is SHA-256.
3. The signature encoding follows the JWS specification for ECDSA.
4. The key arrives as a `PrivateKey` object with a matching type.
5. The JWS header will contain the string `ES256`.
6. The library is the one that defines `SignatureAlgorithm`.

None of these decisions is wrong. All of them are now fixed in a compiled artifact.

The verifier holds a matching set:

```java
Jws<Claims> parsed = Jwts.parserBuilder()
    .setSigningKey(publicKeyFor("ES256"))   // <-- and again here
    .build()
    .parseClaimsJws(token);
```

---

## 3. Before: what the migration costs

Seven steps, in the order a team meets them.

1. **Edit 66 call sites across 6 services.** Each edit is small. The review, test, and release cycle for each service is not.
2. **Add a library that speaks ML-DSA.** The current JWT library does not. Either a new library arrives or the team writes composite handling by hand.
3. **Grow the JWKS document.** An ML-DSA-65 public key is 1,952 bytes against 32 bytes for the P-256 key. The published key set grows from under a kilobyte to roughly 8 KB. Every client that caches it must tolerate the new size.
4. **Rewrite JWS header handling.** No registered `alg` value describes this composite. The team either waits for a registration or invents a private value, and a private value breaks interoperability by definition.
5. **Coordinate four relying party groups.** Each must verify the new algorithm before the issuer may produce it. One group runs software the organization does not control.
6. **Build six deployments and six rollback plans.** Each service ships independently, and each needs a path back.
7. **Repeat all of it for the next algorithm.** The parameter set will change. ML-DSA-65 is not the last value this field will hold.

An estimate of three quarters of engineering time is realistic for this shape of work, and the last step is the one that hurts. The seventh step means the six preceding steps were not an investment. They were rent.

---

## 4. After: the algorithm leaves the call

```java
// TokenIssuer.java  —  and this is the only shape, everywhere
public String issueAccessToken(Subject subject, Set<String> scopes) {
    byte[] payload = claims(subject, scopes);
    SignResult r = crypto.sign(handle("idp-access-token"), payload);
    return jws(r.protectedHeader(), payload, r.signature());
}
```

Zero algorithm decisions remain in the call.

The handle `idp-access-token` names an intent. The broker resolves that intent against the active policy profile. The returned `protectedHeader` carries whatever `alg` value the resolution produced, so the caller does not construct it.

The verifier changes in the same way:

```java
VerifyResult v = crypto.verify(publicMaterial(kid), payload, signature);
```

### 4.1 The policy profile that drives it

```yaml
profile: idp-signing
version: 2026.08.1
effective: 2026-09-01T00:00:00Z
expires:   2027-09-01T00:00:00Z

intents:
  idp-access-token:
    algorithm: id-composite-ecdsa-p256-mldsa65
    minimum_strength: 128
    lifecycle: active
    providers:
      ecdsa-p256: hsm-pool-primary      # FIPS validated hardware
      mldsa65:    liboqs-software       # no HSM firmware wait

  idp-refresh-token:
    algorithm: ES256
    minimum_strength: 128
    lifecycle: deprecated
    deprecated_after: 2027-01-01T00:00:00Z
```

Two details in that profile do real work.

The `providers` block splits one signature across a hardware backend and a software backend. The organization gets a hybrid signature without waiting for HSM firmware to support ML-DSA. Section 4 of the architecture document describes the mechanism.

The `minimum_strength` field lets resolution reject a downgrade. If a later profile edit tries to select a weaker algorithm, resolution fails rather than complying.

### 4.2 What the migration costs now

1. Edit one policy profile.
2. Sign the profile.
3. Publish it.

No service is rebuilt. No call site is edited. No library is added, because the broker owns the composite path.

---

## 5. What did not change, and why that is the point

The call signature did not change. The handle did not change. The stored reference in the token service database did not change. The audit schema did not change.

A team can run `ResolvePolicy("idp-access-token")` in a pipeline test and assert the expected algorithm before any traffic moves. A policy change becomes something a test catches.

The second migration then costs the same three steps as the first. That property, not the first migration, is the return on the architecture.

---

## 6. What still costs work

This section exists because a migration document without it is marketing.

**Relying parties must move first.** The issuer cannot produce a signature nobody verifies. The order is fixed: verifiers gain the capability, then policy switches the issuer. The broker gives the issuer a single switch and gives the verifiers nothing.

**The JWKS document is still 8 KB.** A larger public key is larger. The broker changes who decides the algorithm and not what the algorithm costs on the wire. Clients with tight caches still feel it.

**A composite identifier needs a registry entry.** Until `id-composite-ecdsa-p256-mldsa65` has a registered byte encoding, two implementations can agree on the algorithms and still disagree on the bytes. Section 9 of the framework document treats this as the interoperability failure point.

**Someone must run the broker.** Under a central topology the broker is now on the token issuance path. That is a new availability dependency and a new latency line. No published measurement exists for this load, which is the strongest reason to build the reference implementation before promising a number.

**The first integration is not free.** Routing 66 call sites through a new API is the same volume of edits as changing the algorithm once. The difference is that this edit happens once and the algorithm edits stop.

---

## 7. The honest summary

The broker does not make cryptography easier. It does not remove coordination. It does not shrink a post-quantum key.

It converts a recurring code change into a recurring configuration change. Under NIST IR 8547 the industry faces deprecation in 2030 and disallowance in 2035, and parameter sets will keep moving after that. The value of this architecture is not the first migration. It is that the fifth one costs an afternoon.

---

*Continue to [the prior art comparison](05-prior-art.md).*
