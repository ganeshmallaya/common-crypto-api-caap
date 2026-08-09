# Experimental schemas

These JSON Schema 2020-12 documents support the `2.0.0` research slice.
The OpenAPI document is the research HTTP binding. The prose specification
controls when a schema cannot express a semantic requirement.

The request schema uses operation-specific conditional validation rather than
accepting an arbitrary `input` object. Repository tests validate checked-in
examples and reference-service requests against these schemas.

`algorithm-profile.schema.json` defines source-backed profile records;
`operation-registry.schema.json` defines the cross-family maturity and behavior
index. Both remain experimental knowledge-base inputs rather than policy.

The schemas are not a normative wire format or a conformance claim. Promotion
still requires canonical vectors, compatibility rules and independent
implementation results.
