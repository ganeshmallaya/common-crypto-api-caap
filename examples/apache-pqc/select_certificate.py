#!/usr/bin/env python3
"""Resolve the Apache certificate through CALI and render a TLS fragment."""

from __future__ import annotations

import argparse
import json
import os
import tempfile
import urllib.error
import urllib.request
from pathlib import Path


CERTIFICATES = {
    "certificate:apache:localhost:ecdsa": ("ecdsa-cert.pem", "ecdsa-key.pem"),
    "certificate:apache:localhost:mldsa65": ("mldsa65-cert.pem", "mldsa65-key.pem"),
}


def select(api_url: str, policy_version: str) -> dict:
    request = {
        "apiVersion": "2.0.0",
        "requestId": "apache-certificate-selection",
        "operation": "SelectCertificate",
        "intent": "apache-tls",
        "expectedPolicy": {
            "profileId": "apache-pqc-migration",
            "profileVersion": policy_version,
        },
        "minimumConstraints": {"profile": "apache-pqc-migration"},
        "input": {"hostname": "localhost"},
    }
    body = json.dumps(request).encode()
    http_request = urllib.request.Request(
        f"{api_url.rstrip('/')}/v2/certificates:select",
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(http_request) as response:
            return json.load(response)
    except urllib.error.HTTPError as exc:
        error = json.load(exc)
        raise RuntimeError(json.dumps(error, indent=2)) from exc


def render_fragment(result: dict, certificate_dir: Path, output: Path) -> None:
    certificate_ref = result["result"]["certificateRef"]
    if certificate_ref not in CERTIFICATES:
        raise ValueError("broker returned an unmapped certificate reference")
    certificate_name, key_name = CERTIFICATES[certificate_ref]
    certificate = (certificate_dir / certificate_name).resolve()
    key = (certificate_dir / key_name).resolve()
    if not certificate.is_file() or not key.is_file():
        raise FileNotFoundError("selected certificate files are not present")
    fragment = (
        f'SSLCertificateFile "{certificate}"\n'
        f'SSLCertificateKeyFile "{key}"\n'
        f'# CALI evidence: {result["evidence"]["evidenceId"]}\n'
        f'# CALI profile: {result["result"]["profile"]}\n'
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix="cali-apache-", dir=output.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            handle.write(fragment)
        os.replace(temporary, output)
    except BaseException:
        Path(temporary).unlink(missing_ok=True)
        raise


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--api-url", default="http://127.0.0.1:8080")
    parser.add_argument("--policy-version", required=True)
    parser.add_argument("--certificate-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    response = select(args.api_url, args.policy_version)
    render_fragment(response, args.certificate_dir, args.output)
    print(json.dumps(response, indent=2))


if __name__ == "__main__":
    main()
