import base64
import sys
import unittest
from datetime import datetime
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker
from referencing import Registry, Resource
from referencing.jsonschema import DRAFT202012


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "reference"))

from caap_reference.broker import API_VERSION, Broker, CaapError, POLICY, RECOGNIZED_EXECUTION_OPERATIONS  # noqa: E402


def request(operation, input_data, request_id="test-request-0001", constraints=None):
    return {
        "apiVersion": API_VERSION,
        "requestId": request_id,
        "operation": operation,
        "intent": "artifact-signing",
        "expectedPolicy": POLICY,
        "minimumConstraints": constraints or {"profile": "artifact-signing-v0", "providerClasses": ["software"]},
        "input": input_data,
    }


class BrokerTest(unittest.TestCase):
    def setUp(self):
        self.broker = Broker()

    def create_key(self):
        status, response = self.broker.execute(request("CreateKey", {"purpose": "sign"}), "tenant-a")
        self.assertEqual(status, 201)
        return response["result"]["keyRef"]

    def assert_openapi_schema(self, name, value):
        api = __import__("json").loads((ROOT / "api/openapi/caap-v1.openapi.json").read_text())
        resource = Resource.from_contents(api, default_specification=DRAFT202012)
        registry = Registry().with_resource("urn:caap:openapi", resource)
        schema = {"$ref": f"urn:caap:openapi#/components/schemas/{name}"}
        Draft202012Validator(schema, registry=registry, format_checker=FormatChecker()).validate(value)

    def test_create_sign_verify(self):
        key_ref = self.create_key()
        message = base64.b64encode(b"release artifact").decode().rstrip("=")
        _, signed = self.broker.execute(request("Sign", {"keyRef": key_ref, "message": message}, "test-request-0002"), "tenant-a")
        _, verified = self.broker.execute(request("Verify", {"keyRef": key_ref, "message": message, "signature": signed["result"]["signature"]}, "test-request-0003"), "tenant-a")
        self.assertTrue(verified["result"]["valid"])
        self.assertEqual(verified["decision"]["policy"], POLICY)
        self.assertEqual(len(self.broker.audit_events), 3)

    def test_modified_message_is_not_valid(self):
        key_ref = self.create_key()
        message = base64.b64encode(b"original").decode().rstrip("=")
        _, signed = self.broker.execute(request("Sign", {"keyRef": key_ref, "message": message}, "test-request-0002"), "tenant-a")
        changed = base64.b64encode(b"changed").decode().rstrip("=")
        _, verified = self.broker.execute(request("Verify", {"keyRef": key_ref, "message": changed, "signature": signed["result"]["signature"]}, "test-request-0003"), "tenant-a")
        self.assertFalse(verified["result"]["valid"])

    def test_key_reference_is_tenant_bound(self):
        key_ref = self.create_key()
        with self.assertRaises(CaapError) as raised:
            self.broker.read_key(key_ref, "tenant-b")
        self.assertEqual(raised.exception.category, "KEY_STATE_INVALID")

    def test_provider_constraint_fails_closed(self):
        with self.assertRaises(CaapError) as raised:
            self.broker.execute(request("ResolvePolicy", {}, constraints={"profile": "artifact-signing-v0", "providerClasses": ["hsm"]}), "tenant-a")
        self.assertEqual(raised.exception.category, "CAPABILITY_MISMATCH")

    def test_policy_version_is_pinned(self):
        value = request("ResolvePolicy", {})
        value["expectedPolicy"] = {"profileId": "baseline-artifact-signing", "profileVersion": "0"}
        with self.assertRaises(CaapError) as raised:
            self.broker.execute(value, "tenant-a")
        self.assertEqual(raised.exception.category, "POLICY_INACTIVE")

    def test_unknown_fields_are_rejected(self):
        value = request("ResolvePolicy", {})
        value["algorithm"] = "choose-for-me"
        with self.assertRaises(CaapError) as raised:
            self.broker.execute(value, "tenant-a")
        self.assertEqual(raised.exception.category, "INVALID_REQUEST")

    def test_known_unimplemented_and_unknown_operations_differ(self):
        known = request("Encrypt", {"keyRef": "key_unavailable", "plaintext": "YQ"})
        with self.assertRaises(CaapError) as raised:
            self.broker.execute(known, "tenant-a")
        self.assertEqual(raised.exception.category, "NOT_IMPLEMENTED")
        self.assertEqual(raised.exception.status, 501)

        unknown = request("DoSomethingCryptographic", {})
        with self.assertRaises(CaapError) as raised:
            self.broker.execute(unknown, "tenant-a")
        self.assertEqual(raised.exception.category, "INVALID_REQUEST")

    def test_rejected_request_records_non_secret_failure_evidence(self):
        value = request("ResolvePolicy", {})
        value["expectedPolicy"] = {"profileId": "baseline-artifact-signing", "profileVersion": "old"}
        with self.assertRaises(CaapError):
            self.broker.execute(value, "tenant-a")
        event = self.broker.audit_events[-1]
        self.assertEqual(event["outcome"], "failure")
        self.assertEqual(event["category"], "POLICY_INACTIVE")
        self.assertNotIn("expectedPolicy", event)

    def test_padded_base64_is_rejected(self):
        key_ref = self.create_key()
        with self.assertRaises(CaapError) as raised:
            self.broker.execute(request("Sign", {"keyRef": key_ref, "message": "YQ=="}, "test-request-0002"), "tenant-a")
        self.assertEqual(raised.exception.category, "INVALID_REQUEST")

    def test_capabilities_are_scoped_and_freshness_bounded(self):
        capabilities = self.broker.capabilities("tenant-a")
        self.assertEqual(capabilities["scope"], {"tenant": "tenant-a", "audience": "caller"})
        self.assertLess(datetime.fromisoformat(capabilities["generatedAt"].replace("Z", "+00:00")), datetime.fromisoformat(capabilities["validUntil"].replace("Z", "+00:00")))
        profile = capabilities["profiles"][0]
        self.assertEqual(profile["providerRef"], "software:python-cryptography")
        self.assertEqual(profile["keyProtections"], ["software-memory"])
        self.assertIn("no-idempotency-store", capabilities["limitations"])

    def test_registry_execution_operations_are_recognized(self):
        import json

        registry = json.loads((ROOT / "api/operation-registry.json").read_text())
        execution = {item["name"] for item in registry["operations"] if item["requestClass"] == "execution"}
        self.assertEqual(execution, RECOGNIZED_EXECUTION_OPERATIONS)

    def test_reference_outputs_match_openapi_schemas(self):
        capabilities = self.broker.capabilities("tenant-a")
        self.assert_openapi_schema("CapabilityResponse", capabilities)

        _, created = self.broker.execute(request("CreateKey", {"purpose": "sign"}), "tenant-a")
        self.assert_openapi_schema("CreateKeyResponse", created)
        key_ref = created["result"]["keyRef"]
        message = base64.b64encode(b"contract evidence").decode().rstrip("=")
        _, signed = self.broker.execute(request("Sign", {"keyRef": key_ref, "message": message}, "schema-sign-0001"), "tenant-a")
        self.assert_openapi_schema("SignResponse", signed)
        _, verified = self.broker.execute(request("Verify", {"keyRef": key_ref, "message": message, "signature": signed["result"]["signature"]}, "schema-verify-01"), "tenant-a")
        self.assert_openapi_schema("VerifyResponse", verified)

        try:
            self.broker.execute(request("UnknownOperation", {}), "tenant-a")
        except CaapError as error:
            self.assert_openapi_schema("ErrorEnvelope", error.response())


if __name__ == "__main__":
    unittest.main()
