"""Policy loading and evaluation for the CALI reference broker."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


class PolicyLoadError(ValueError):
    """Raised when a configured policy cannot be trusted or evaluated."""


def load_policy(path: str | Path) -> dict[str, Any]:
    policy_path = Path(path)
    try:
        value = json.loads(policy_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise PolicyLoadError(f"cannot load policy file {policy_path}") from exc
    _validate_policy(value)
    return value


def _parse_time(value: Any, field: str) -> datetime:
    if not isinstance(value, str):
        raise PolicyLoadError(f"{field} must be an RFC 3339 timestamp")
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise PolicyLoadError(f"{field} must be an RFC 3339 timestamp") from exc


def _validate_policy(value: Any) -> None:
    if not isinstance(value, dict):
        raise PolicyLoadError("policy must be a JSON object")
    required = {
        "schemaVersion",
        "profileId",
        "profileVersion",
        "status",
        "effectiveAt",
        "expiresAt",
        "rules",
    }
    if set(value) != required:
        raise PolicyLoadError("policy fields do not match the reference contract")
    if value["schemaVersion"] != "2.0.0" or value["status"] != "active":
        raise PolicyLoadError("policy must use schemaVersion 2.0.0 and active status")
    now = datetime.now(UTC)
    if _parse_time(value["effectiveAt"], "effectiveAt") > now:
        raise PolicyLoadError("policy is not effective yet")
    if value["expiresAt"] is not None and _parse_time(value["expiresAt"], "expiresAt") <= now:
        raise PolicyLoadError("policy has expired")
    if not isinstance(value["rules"], list) or not value["rules"]:
        raise PolicyLoadError("policy must contain at least one rule")


def resolve_certificate_policy(
    policy: dict[str, Any],
    hostname: str,
    available_profiles: set[str],
) -> tuple[dict[str, str], dict[str, str]]:
    matches = [
        rule
        for rule in policy["rules"]
        if rule.get("intent") == "apache-tls"
        and rule.get("operation") == "SelectCertificate"
        and hostname in rule.get("hostnames", [])
    ]
    if not matches:
        raise PolicyLoadError("no active certificate policy matches this hostname")
    if len(matches) != 1:
        raise PolicyLoadError("more than one certificate policy matches this hostname")
    rule = matches[0]
    choices = rule.get("choices")
    if not isinstance(choices, list) or not choices:
        raise PolicyLoadError("certificate policy has no choices")
    for choice in choices:
        if choice.get("profile") in available_profiles:
            decision = {
                "profileId": policy["profileId"],
                "profileVersion": policy["profileVersion"],
                "ruleId": rule["ruleId"],
            }
            return decision, choice
    raise PolicyLoadError("no policy approved certificate profile is available")
