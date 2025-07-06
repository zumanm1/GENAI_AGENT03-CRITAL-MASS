"""Simple network configuration validator and dry-run predictor.

This is **not** a full parser.  It performs lightweight checks so that the
0700 Configuration Validation feature is demonstrably functional without
adding heavyweight external dependencies (e.g. Batfish).  It can be
extended or swapped later.
"""
from __future__ import annotations

from typing import Any, Dict, List, Tuple

try:
    from ciscoconfparse import CiscoConfParse  # type: ignore
    _CISCOCONFAVAILABLE = True
except ImportError:
    _CISCOCONFAVAILABLE = False

# ---------------------------------------------------------------------------
# Helper rules per device OS
# ---------------------------------------------------------------------------
# Very small, illustrative keyword sets for demo purposes.
# A real implementation would load comprehensive grammars or invoke an
# external engine.
SUPPORTED_OSES = {
    "cisco_ios": {
        "keywords": {
            "interface", "router", "ip", "hostname", "line", "enable",
            "access-list", "no", "vlan", "username", "password",
        },
        "comment": "!",
    },
    "juniper_junos": {
        "keywords": {
            "set", "delete", "interfaces", "protocols", "system",
            "routing-options", "security", "firewall", "policy-options",
        },
        "comment": "#",
    },
    "arista_eos": {
        "keywords": {
            "interface", "hostname", "ip", "vlan", "username",
            "enable", "no", "router", "management", "service-policy",
        },
        "comment": "!",
    },
    # For the others, fall back to IOS-style rules
    "cisco_nxos": {},
    "cisco_xr": {},
}

# Default comment char if not specified
DEFAULT_COMMENT = "!"


class ValidationResult(dict):
    """Lightweight container with dot-access helpers."""

    @property
    def errors(self) -> List[str]:
        return self.get("errors", [])

    @property
    def warnings(self) -> List[str]:
        return self.get("warnings", [])

    @property
    def actions(self) -> List[Dict]:
        return self.get("dry_run", {}).get("actions", [])


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def _validate_cisco_ios(config_text: str) -> Tuple[List[str], List[str]]:
    """Deep-validate Cisco IOS config using CiscoConfParse when available."""
    if not _CISCOCONFAVAILABLE:
        # Fallback to keyword validation only
        return _simple_keyword_validation("cisco_ios", config_text)

    parse = CiscoConfParse(config_text.splitlines(keepends=True))
    errors: List[str] = []
    actions: List[str] = []

    # Example rule: ensure every interface has description
    for intf in parse.find_objects(r"^interface "):
        if not intf.re_search_children(r"description "):
            errors.append(
                f"Interface '{intf.text.strip()}' missing description")

    # Example rule: detect duplicate IP addresses
    ip_addresses = {}
    for intf in parse.find_objects(r"^interface "):
        ip_commands = intf.re_search_children(r"ip address ")
        for cmd in ip_commands:
            parts = cmd.text.strip().split()
            if len(parts) >= 3:
                ip = parts[2] if parts[1] == "address" else None
                if ip:
                    if ip in ip_addresses:
                        errors.append(
                            f"Duplicate IP {ip} on {intf.text.strip()} "
                            f"(also on {ip_addresses[ip]})"
                        )
                    else:
                        ip_addresses[ip] = intf.text.strip()

    # Very naive dry-run: treat each line as ADD/REMOVE
    for line in config_text.splitlines():
        if not line.strip() or line.strip().startswith("!"):
            continue
        if line.lstrip().startswith("no "):
            actions.append(f"REMOVE {line.strip()[3:]}")
        else:
            actions.append(f"ADD {line.strip()}")

    return errors, actions


def _simple_keyword_validation(
    device_type: str, config_text: str
) -> Tuple[List[str], List[str]]:
    device_rules = SUPPORTED_OSES[device_type]
    errors: List[str] = []
    actions: List[str] = []
    lines = [
        line.strip()
        for line in config_text.splitlines()
        if line.strip() and not line.strip().startswith("!")
    ]

    for line in lines:
        keyword = line.split()[0]
        if keyword not in device_rules["keywords"]:
            errors.append(f"Unknown keyword '{keyword}' in line: {line}")

        if line.startswith("no "):
            actions.append(f"REMOVE {line[3:]}")
        else:
            actions.append(f"ADD {line}")

    return errors, actions


def validate_config(
    device_type: str, config_text: str
) -> Dict[str, Any]:
    """Validate config_text for device_type and return structured result."""

    if device_type == "cisco_ios":
        errors, actions = _validate_cisco_ios(config_text)
    elif device_type in SUPPORTED_OSES:
        errors, actions = _simple_keyword_validation(device_type, config_text)
    else:
        return {
            "status": "failed",
            "errors": [f"Unsupported device type: {device_type}"],
            "dry_run": {"actions": []},
        }

    status = "success" if not errors else "failed"
    return {
        "status": status,
        "errors": errors,
        "dry_run": {"actions": actions},
    }
