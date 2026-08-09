import json
import re
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker
from jsonschema.exceptions import ValidationError
from openapi_spec_validator import validate


ROOT = Path(__file__).resolve().parents[1]


class RepositoryContractTest(unittest.TestCase):
    def test_all_json_files_parse(self):
        for path in sorted(ROOT.rglob("*.json")):
            if ".local-backup" in path.parts:
                continue
            with self.subTest(path=path.relative_to(ROOT)):
                json.loads(path.read_text(encoding="utf-8"))

    def test_json_schemas_and_examples_validate(self):
        request_schema = json.loads((ROOT / "schemas/protocol-envelope.schema.json").read_text())
        policy_schema = json.loads((ROOT / "schemas/policy-profile.schema.json").read_text())
        registry_schema = json.loads((ROOT / "schemas/operation-registry.schema.json").read_text())
        algorithm_profile_schema = json.loads((ROOT / "schemas/algorithm-profile.schema.json").read_text())
        Draft202012Validator.check_schema(request_schema)
        Draft202012Validator.check_schema(policy_schema)
        Draft202012Validator.check_schema(registry_schema)
        Draft202012Validator.check_schema(algorithm_profile_schema)
        Draft202012Validator(request_schema, format_checker=FormatChecker()).validate(
            json.loads((ROOT / "examples/create-key.example.json").read_text())
        )
        Draft202012Validator(policy_schema, format_checker=FormatChecker()).validate(
            json.loads((ROOT / "examples/policy-profile.example.json").read_text())
        )
        registry = json.loads((ROOT / "api/operation-registry.json").read_text())
        Draft202012Validator(registry_schema).validate(registry)
        names = [operation["name"] for operation in registry["operations"]]
        self.assertEqual(len(names), len(set(names)))
        profiles = []
        for path in sorted((ROOT / "api/profiles").glob("*.profile.json")):
            profile = json.loads(path.read_text())
            Draft202012Validator(algorithm_profile_schema, format_checker=FormatChecker()).validate(profile)
            profiles.append(profile)
        algorithm_profile = next(profile for profile in profiles if profile["profileId"] == "artifact-signing-v0")
        policy = json.loads((ROOT / "examples/policy-profile.example.json").read_text())
        self.assertEqual(policy["rules"][0]["decision"]["profile"], algorithm_profile["profileId"])
        self.assertEqual(policy["rules"][0]["decision"]["algorithm"], algorithm_profile["algorithms"][0]["identifier"])

        invalid = json.loads((ROOT / "examples/create-key.example.json").read_text())
        invalid["input"]["exportable"] = True
        with self.assertRaises(ValidationError):
            Draft202012Validator(request_schema).validate(invalid)

    def test_canonical_naming(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("Cryptographic Abstraction Layer Interface (CALI)", readme)
        self.assertIn("**Common Crypto API**", readme)

    def test_canonical_site_integration_is_consistent(self):
        canonical = "https://ganeshmallaya.com/research/crypto-agility-algorithm-protocol/"
        for relative in ("README.md", "docs/personal-site-integration.md"):
            self.assertIn(canonical, (ROOT / relative).read_text(encoding="utf-8"))
        self.assertFalse((ROOT / "site").exists())
        self.assertFalse((ROOT / "integration").exists())

    def test_public_work_has_no_named_commercial_research_reference(self):
        terms = ("i" + "bm", "agile" + "-crypto", "ci" + "tius")
        for path in sorted(ROOT.rglob("*")):
            if not path.is_file() or ".git" in path.parts or ".local-backup" in path.parts or ".venv" in path.parts:
                continue
            if path.suffix.lower() not in {".md", ".html", ".css", ".js", ".json", ".py", ".yml", ".toml"}:
                continue
            with self.subTest(path=path.relative_to(ROOT)):
                content = path.read_text(encoding="utf-8").lower()
                for term in terms:
                    self.assertNotIn(term, content)

    def test_openapi_vertical_slice(self):
        api = json.loads((ROOT / "api/openapi/cali-v2.openapi.json").read_text())
        validate(api)
        self.assertEqual(api["openapi"], "3.1.0")
        self.assertEqual(api["info"]["version"], "2.0.0-draft")
        self.assertEqual(
            set(api["paths"]),
            {"/healthz", "/v2/capabilities", "/v2/policies:resolve", "/v2/keys", "/v2/keys/{keyRef}", "/v2/sign", "/v2/verify"},
        )

    def test_openapi_operations_are_typed_and_maturity_labelled(self):
        api = json.loads((ROOT / "api/openapi/cali-v2.openapi.json").read_text())
        expected = {
            "resolvePolicy": "ResolvePolicyRequest",
            "createKey": "CreateKeyRequest",
            "sign": "SignRequest",
            "verify": "VerifyRequest",
        }
        for path_item in api["paths"].values():
            for method, operation in path_item.items():
                if method not in {"get", "post"}:
                    continue
                self.assertEqual(operation["x-cali-maturity"], "implemented")
                operation_id = operation["operationId"]
                if operation_id in expected:
                    reference = operation["requestBody"]["$ref"]
                    self.assertEqual(reference, f"#/components/requestBodies/{expected[operation_id]}")
        categories = set(api["components"]["schemas"]["ErrorCategory"]["enum"])
        self.assertTrue({"POLICY_AMBIGUOUS", "CAPABILITY_MISMATCH", "IDEMPOTENCY_CONFLICT", "AUTHENTICATION_FAILED"} <= categories)

    def test_openapi_internal_references_resolve(self):
        api = json.loads((ROOT / "api/openapi/cali-v2.openapi.json").read_text())

        def walk(value):
            if isinstance(value, dict):
                if "$ref" in value and value["$ref"].startswith("#/"):
                    target = api
                    for part in value["$ref"][2:].split("/"):
                        target = target[part.replace("~1", "/").replace("~0", "~")]
                for child in value.values():
                    walk(child)
            elif isinstance(value, list):
                for child in value:
                    walk(child)

        walk(api)

    def test_operation_contract_covers_requested_surface(self):
        contract = (ROOT / "spec/operation-contracts.md").read_text(encoding="utf-8")
        registry = json.loads((ROOT / "api/operation-registry.json").read_text())
        registered = {item["name"] for item in registry["operations"]}
        operations = {
            "Encrypt", "Decrypt", "GenerateMac", "VerifyMac", "DeriveKey",
            "AgreeKey", "Encapsulate", "Decapsulate", "WrapKey", "UnwrapKey",
            "RotateKey", "TransformKey", "MigrateKey", "GetCapabilities",
            "ResolvePolicy", "CreateKey", "Sign", "Verify",
        }
        for operation in operations:
            with self.subTest(operation=operation):
                self.assertIn(f"`{operation}`", contract)
                self.assertIn(operation, registered)
        for topic in ("PKCS#11", "KMIP", "Local-library", "Persistent stores", "Hierarchical evaluation", "idempotency"):
            with self.subTest(topic=topic):
                self.assertIn(topic, contract)

    def test_public_repository_governance_files_exist(self):
        for relative in ("NOTICE.md", "SECURITY.md", "CONTRIBUTING.md"):
            self.assertTrue((ROOT / relative).is_file())

    def test_no_tracked_legacy_public_export_contract(self):
        self.assertFalse((ROOT / "public-export").exists())
        self.assertFalse((ROOT / "common-crypto-api-spec-draft-v0.1.md").exists())

    def test_independent_development_disclaimer_is_public(self):
        for relative in ("README.md", "NOTICE.md"):
            text = (ROOT / relative).read_text(encoding="utf-8")
            self.assertIn("no affiliation with", text)

    def test_relative_markdown_links_resolve(self):
        link = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
        for path in sorted(ROOT.rglob("*.md")):
            if ".local-backup" in path.parts:
                continue
            for target in link.findall(path.read_text(encoding="utf-8")):
                if target.startswith(("http://", "https://", "#", "mailto:")):
                    continue
                relative = target.split("#", 1)[0]
                if relative:
                    with self.subTest(path=path.relative_to(ROOT), target=target):
                        self.assertTrue((path.parent / relative).exists())


if __name__ == "__main__":
    unittest.main()
