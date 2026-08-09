import hashlib
import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCHEMAS = ROOT / "schemas"
EXAMPLES = ROOT / "examples"
PUBLIC_EXPORT = ROOT / "public-export"


class JsonArtifactsTest(unittest.TestCase):
    def test_all_json_files_parse(self):
        for path in sorted(ROOT.rglob("*.json")):
            with self.subTest(path=path.relative_to(ROOT)):
                with path.open(encoding="utf-8") as handle:
                    json.load(handle)

    def test_schema_documents_declare_draft_2020_12(self):
        for path in sorted(SCHEMAS.glob("*.schema.json")):
            with self.subTest(path=path.name):
                data = json.loads(path.read_text(encoding="utf-8"))
                self.assertEqual(
                    data.get("$schema"),
                    "https://json-schema.org/draft/2020-12/schema",
                )
                self.assertTrue(data.get("$id", "").startswith("https://example.invalid/"))

    def test_examples_use_non_production_namespace(self):
        for path in sorted(EXAMPLES.glob("*.json")):
            with self.subTest(path=path.name):
                text = path.read_text(encoding="utf-8")
                if '"namespace"' in text:
                    self.assertIn("https://example.invalid/", text)


class PublicExportTest(unittest.TestCase):
    def setUp(self):
        self.manifest = json.loads(
            (PUBLIC_EXPORT / "site-manifest.json").read_text(encoding="utf-8")
        )

    def test_canonical_naming(self):
        project = self.manifest["project"]
        self.assertEqual(project["canonicalName"], "Crypto Agility Algorithm Protocol")
        self.assertEqual(project["abbreviation"], "CAAP")
        self.assertEqual(project["interfaceName"], "Common Crypto API")
        self.assertEqual(project["repository"], "common-crypto-api-caap")

    def test_expected_website_routes(self):
        self.assertEqual(
            self.manifest["targets"],
            [
                "/research/",
                "/research/crypto-agility-algorithm-protocol/",
            ],
        )

    def test_allowlisted_files_exist_and_stay_inside_export(self):
        for entry in self.manifest["files"]:
            with self.subTest(path=entry["path"]):
                relative = Path(entry["path"])
                self.assertFalse(relative.is_absolute())
                self.assertNotIn("..", relative.parts)
                path = (PUBLIC_EXPORT / relative).resolve()
                self.assertTrue(path.is_relative_to(PUBLIC_EXPORT.resolve()))
                self.assertTrue(path.is_file())

    def test_publication_gate(self):
        status = self.manifest["status"]
        self.assertIn(status, {"draft", "reviewed", "published", "withdrawn"})
        if status in {"reviewed", "published"}:
            self.assertRegex(self.manifest["sourceCommit"], r"^[0-9a-f]{40}([0-9a-f]{24})?$")
            self.assertIsInstance(self.manifest["review"]["reviewedBy"], str)
            self.assertTrue(self.manifest["review"]["reviewedBy"].strip())
            self.assertIsInstance(self.manifest["review"]["reviewedAt"], str)
            for entry in self.manifest["files"]:
                expected = hashlib.sha256(
                    (PUBLIC_EXPORT / entry["path"]).read_bytes()
                ).hexdigest()
                self.assertEqual(entry["contentSha256"], expected)
        else:
            self.assertIsNone(self.manifest["sourceCommit"])

    def test_site_summary_has_canonical_heading(self):
        summary = (PUBLIC_EXPORT / "site-summary.md").read_text(encoding="utf-8")
        self.assertTrue(
            summary.startswith("# Crypto Agility Algorithm Protocol (CAAP)\n")
        )


class MarkdownLinkTest(unittest.TestCase):
    LINK = re.compile(r"\[[^\]]+\]\(([^)]+)\)")

    def test_relative_markdown_links_resolve(self):
        for path in sorted(ROOT.rglob("*.md")):
            for target in self.LINK.findall(path.read_text(encoding="utf-8")):
                if target.startswith(("http://", "https://", "#", "mailto:")):
                    continue
                target_path = target.split("#", 1)[0]
                if not target_path:
                    continue
                with self.subTest(path=path.relative_to(ROOT), target=target):
                    self.assertTrue((path.parent / target_path).exists())


if __name__ == "__main__":
    unittest.main()
