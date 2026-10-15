"""Output formatting utilities for CLI.

SPDX-License-Identifier: GPL-3.0-or-later
"""

import json
from typing import Any, Dict, List


def format_json(data: Any) -> str:
    """Format data as JSON.

    Args:
        data: Data to format (dict, list, or other)

    Returns:
        JSON string
    """
    return json.dumps(data, indent=2)


def format_table(data: Dict[str, Dict]) -> str:
    """Format service data as an ASCII table.

    Args:
        data: Dict mapping service IDs to configurations

    Returns:
        Formatted table string
    """
    if not data:
        return "No services registered."

    # Calculate column widths
    id_width = max(len("SERVICE ID"), max(len(sid) for sid in data.keys())) + 2
    host_width = max(len("HOST"), max(len(info["host"]) for info in data.values())) + 2
    port_width = max(len("PORT"), 6) + 2  # At least "PORT  " wide
    proto_width = max(len("PROTOCOL"), max(len(info.get("protocol", "http")) for info in data.values())) + 2

    # Build table
    lines = []

    # Header
    header = f"{'SERVICE ID':<{id_width}} {'HOST':<{host_width}} {'PORT':<{port_width}} {'PROTOCOL':<{proto_width}}"
    lines.append(header)
    lines.append("-" * len(header))

    # Rows
    for service_id, info in sorted(data.items()):
        host = info.get("host", "")
        port = info.get("port", "")
        protocol = info.get("protocol", "http")
        line = f"{service_id:<{id_width}} {host:<{host_width}} {port:<{port_width}} {protocol:<{proto_width}}"
        lines.append(line)

    return "\n".join(lines)
