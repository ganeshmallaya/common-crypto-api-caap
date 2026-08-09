"""Minimal CAAP broker and software provider for the artifact-signing profile."""

from __future__ import annotations

import base64
import binascii
import hashlib
import json
import secrets
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import Any

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey


API_VERSION = "0.2.0-draft"
PROFILE = "artifact-signing-v0"
ALGORITHM = "http://www.w3.org/2021/04/xmldsig-more#eddsa-ed25519"
POLICY = {"profileId": "baseline-artifact-signing", "profileVersion": "1"}
PROVIDER_REF = "software:python-cryptography"
RECOGNIZED_EXECUTION_OPERATIONS = {
    "ResolvePolicy", "DryRunPolicy", "CreateKey", "RotateKey", "TransformKey",
    "MigrateKey", "ImportKey", "ExportKey", "SetKeyState", "DestroyKey",
    "Sign", "Verify", "SignDigest", "VerifyDigest", "GenerateMac", "VerifyMac",
    "Encrypt", "Decrypt", "Digest", "ExpandOutput", "GenerateRandom",
    "DeriveKey", "DeriveBytes", "AgreeKey", "Encapsulate", "Decapsulate",
    "WrapKey", "UnwrapKey", "BeginOperation", "UpdateOperation",
    "FinalizeOperation", "AbortOperation",
}


class CaapError(Exception):
    def __init__(self, category: str, message: str, *, retryable: bool = False, status: int = 400):
        super().__init__(message)
        self.category = category
        self.message = message
        self.retryable = retryable
        self.status = status

    def response(self) -> dict[str, Any]:
        return {"error": {"category": self.category, "message": self.message, "retryable": self.retryable}}


@dataclass
class KeyRecord:
    tenant: str
    key_ref: str
    version: int
    purpose: str
    state: str
    private_key: Ed25519PrivateKey
    created_at: str

    def public_key_b64(self) -> str:
        raw = self.private_key.public_key().public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw,
        )
        return _b64encode(raw)


def _now() -> str:
    return datetime.now(UTC).isoformat().replace("+00:00", "Z")


def _b64encode(value: bytes) -> str:
    return base64.b64encode(value).decode("ascii").rstrip("=")


def _b64decode(value: Any, field: str) -> bytes:
    if not isinstance(value, str) or not value:
        raise CaapError("INVALID_REQUEST", f"{field} must be non-empty unpadded base64")
    if "=" in value:
        raise CaapError("INVALID_REQUEST", f"{field} must use canonical unpadded base64")
    try:
        padded = value + "=" * (-len(value) % 4)
        return base64.b64decode(padded, validate=True)
    except (binascii.Error, ValueError) as exc:
        raise CaapError("INVALID_REQUEST", f"{field} is not valid unpadded base64") from exc


class Broker:
    """In-memory research broker. A new process starts with no keys."""

    def __init__(self) -> None:
        self._keys: dict[str, KeyRecord] = {}
        self.audit_events: list[dict[str, Any]] = []

    def capabilities(self, tenant: str) -> dict[str, Any]:
        generated_at = datetime.now(UTC)
        return {
            "apiVersion": API_VERSION,
            "generatedAt": generated_at.isoformat().replace("+00:00", "Z"),
            "validUntil": (generated_at + timedelta(minutes=5)).isoformat().replace("+00:00", "Z"),
            "scope": {"tenant": tenant, "audience": "caller"},
            "profiles": [{"profile": PROFILE, "operations": ["CreateKey", "Sign", "Verify"], "algorithms": [ALGORITHM], "providerClasses": ["software"], "providerRef": PROVIDER_REF, "keyProtections": ["software-memory"]}],
            "limitations": ["research-only", "in-memory-keys", "single-provider", "no-idempotency-store", "no-conformance-claim"],
        }

    def execute(self, request: dict[str, Any], tenant: str) -> tuple[int, dict[str, Any]]:
        try:
            self._validate_common(request)
            operation = request["operation"]
            if operation == "ResolvePolicy":
                return 200, self._resolve(request, tenant)
            if operation == "CreateKey":
                return 201, self._create_key(request, tenant)
            if operation == "Sign":
                return 200, self._sign(request, tenant)
            if operation == "Verify":
                return 200, self._verify(request, tenant)
            raise CaapError("NOT_IMPLEMENTED", f"operation {operation!r} is recognized but not implemented", status=501)
        except CaapError as exc:
            self._record_failure(request, tenant, exc)
            raise

    def read_key(self, key_ref: str, tenant: str) -> dict[str, Any]:
        key = self._get_key(key_ref, tenant)
        return self._key_metadata(key)

    def _validate_common(self, request: Any) -> None:
        if not isinstance(request, dict):
            raise CaapError("INVALID_REQUEST", "request body must be a JSON object")
        allowed = {"apiVersion", "requestId", "operation", "intent", "expectedPolicy", "minimumConstraints", "input"}
        unknown = sorted(set(request) - allowed)
        if unknown:
            raise CaapError("INVALID_REQUEST", f"unknown fields: {', '.join(unknown)}")
        required = {"apiVersion", "requestId", "operation", "intent", "minimumConstraints", "input"}
        missing = sorted(required - set(request))
        if missing:
            raise CaapError("INVALID_REQUEST", f"missing fields: {', '.join(missing)}")
        if request["apiVersion"] != API_VERSION:
            raise CaapError("INVALID_REQUEST", "unsupported apiVersion")
        request_id = request["requestId"]
        if not isinstance(request_id, str) or not 8 <= len(request_id) <= 128 or not all(c.isalnum() or c in "._:-" for c in request_id):
            raise CaapError("INVALID_REQUEST", "invalid requestId")
        if request["intent"] != "artifact-signing":
            raise CaapError("POLICY_NOT_FOUND", "no policy for requested intent")
        if not isinstance(request["operation"], str) or request["operation"] not in RECOGNIZED_EXECUTION_OPERATIONS:
            raise CaapError("INVALID_REQUEST", "unknown operation")
        if not isinstance(request["minimumConstraints"], dict) or not isinstance(request["input"], dict):
            raise CaapError("INVALID_REQUEST", "minimumConstraints and input must be objects")

    def _decision(self, request: dict[str, Any]) -> dict[str, Any]:
        expected = request.get("expectedPolicy")
        if expected is not None and expected != POLICY:
            raise CaapError("POLICY_INACTIVE", "expected policy is not the active pinned policy")
        constraints = request["minimumConstraints"]
        if constraints.get("profile", PROFILE) != PROFILE:
            raise CaapError("CONSTRAINT_MISMATCH", "requested profile is unsupported")
        allowed_classes = constraints.get("providerClasses", ["software"])
        if not isinstance(allowed_classes, list) or "software" not in allowed_classes:
            raise CaapError("CAPABILITY_MISMATCH", "no allowed provider class can execute this profile")
        unknown = set(constraints) - {"profile", "providerClasses"}
        if unknown:
            raise CaapError("INVALID_REQUEST", f"unknown minimum constraints: {', '.join(sorted(unknown))}")
        return {"policy": POLICY, "profile": PROFILE, "algorithm": ALGORITHM, "providerRef": PROVIDER_REF}

    def _resolve(self, request: dict[str, Any], tenant: str) -> dict[str, Any]:
        if request["input"]:
            raise CaapError("INVALID_REQUEST", "ResolvePolicy input must be empty")
        return self._response(request, tenant, self._decision(request), {"resolved": True})

    def _create_key(self, request: dict[str, Any], tenant: str) -> dict[str, Any]:
        decision = self._decision(request)
        input_data = request["input"]
        if set(input_data) - {"purpose"} or input_data.get("purpose") != "sign":
            raise CaapError("INVALID_REQUEST", "CreateKey requires input.purpose='sign'")
        key = KeyRecord(tenant, "key_" + secrets.token_urlsafe(18), 1, "sign", "active", Ed25519PrivateKey.generate(), _now())
        self._keys[key.key_ref] = key
        return self._response(request, tenant, decision, self._key_metadata(key))

    def _sign(self, request: dict[str, Any], tenant: str) -> dict[str, Any]:
        decision = self._decision(request)
        input_data = request["input"]
        if set(input_data) != {"keyRef", "message"}:
            raise CaapError("INVALID_REQUEST", "Sign input requires only keyRef and message")
        key = self._get_key(input_data["keyRef"], tenant)
        message = _b64decode(input_data["message"], "input.message")
        signature = key.private_key.sign(message)
        return self._response(request, tenant, decision, {"keyRef": key.key_ref, "keyVersion": key.version, "signature": _b64encode(signature), "encoding": "base64-unpadded"})

    def _verify(self, request: dict[str, Any], tenant: str) -> dict[str, Any]:
        decision = self._decision(request)
        input_data = request["input"]
        if set(input_data) != {"keyRef", "message", "signature"}:
            raise CaapError("INVALID_REQUEST", "Verify input requires only keyRef, message, and signature")
        key = self._get_key(input_data["keyRef"], tenant)
        message = _b64decode(input_data["message"], "input.message")
        signature = _b64decode(input_data["signature"], "input.signature")
        try:
            key.private_key.public_key().verify(signature, message)
            valid = True
        except InvalidSignature:
            valid = False
        return self._response(request, tenant, decision, {"keyRef": key.key_ref, "keyVersion": key.version, "valid": valid})

    def _get_key(self, key_ref: Any, tenant: str) -> KeyRecord:
        if not isinstance(key_ref, str):
            raise CaapError("INVALID_REQUEST", "keyRef must be a string")
        key = self._keys.get(key_ref)
        if key is None or key.tenant != tenant:
            raise CaapError("KEY_STATE_INVALID", "key is unavailable for this caller", status=404)
        if key.state != "active" or key.purpose != "sign":
            raise CaapError("KEY_STATE_INVALID", "key state or purpose does not permit this operation")
        return key

    def _key_metadata(self, key: KeyRecord) -> dict[str, Any]:
        return {"keyRef": key.key_ref, "keyVersion": key.version, "purpose": key.purpose, "state": key.state, "profile": PROFILE, "algorithm": ALGORITHM, "providerRef": PROVIDER_REF, "publicKey": key.public_key_b64(), "publicKeyEncoding": "raw-base64-unpadded", "createdAt": key.created_at}

    def _response(self, request: dict[str, Any], tenant: str, decision: dict[str, Any], result: dict[str, Any]) -> dict[str, Any]:
        timestamp = _now()
        event_basis = {"requestId": request["requestId"], "tenant": tenant, "operation": request["operation"], "decision": decision, "timestamp": timestamp}
        evidence_id = "evt_" + hashlib.sha256(json.dumps(event_basis, sort_keys=True, separators=(",", ":")).encode()).hexdigest()[:24]
        event = {**event_basis, "evidenceId": evidence_id}
        self.audit_events.append(event)
        return {"apiVersion": API_VERSION, "requestId": request["requestId"], "operation": request["operation"], "outcome": "success", "decision": decision, "result": result, "evidence": {"evidenceId": evidence_id, "decisionAt": timestamp, "executedAt": timestamp}}

    def _record_failure(self, request: Any, tenant: str, error: CaapError) -> None:
        request_id = request.get("requestId") if isinstance(request, dict) and isinstance(request.get("requestId"), str) else "unavailable"
        operation = request.get("operation") if isinstance(request, dict) and isinstance(request.get("operation"), str) else "unavailable"
        timestamp = _now()
        basis = {"requestId": request_id, "tenant": tenant, "operation": operation, "category": error.category, "timestamp": timestamp}
        self.audit_events.append({**basis, "outcome": "failure", "evidenceId": "evt_" + hashlib.sha256(json.dumps(basis, sort_keys=True, separators=(",", ":")).encode()).hexdigest()[:24]})
