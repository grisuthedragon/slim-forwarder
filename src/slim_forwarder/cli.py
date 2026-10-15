"""CLI entry point for slim-forwarder.

SPDX-License-Identifier: GPL-3.0-or-later
"""

import argparse
import json
import sys
from typing import List, Optional

import yaml

from .api_client import (
    APIClient,
    sync_add_service,
    sync_delete_service,
    sync_list_services,
)
from .output import format_json, format_table


def cmd_register(args: argparse.Namespace) -> int:
    """Handle 'register' subcommand."""
    # Load config from file if provided
    if args.config:
        try:
            with open(args.config, "r") as f:
                config = yaml.safe_load(f)
            # Use config values, override with CLI args
            service_id = args.id or config.get("id") or config.get("service_id")
            host = args.host or config.get("host")
            port = args.port or config.get("port")
            # Only use protocol from config if not specified via CLI
            protocol = config.get("protocol") if args.protocol == "http" else args.protocol
            # Default to http if neither config nor CLI provides it
            protocol = protocol or "http"
            # Get tags from config or CLI (CLI tags override config)
            tags = config.get("tags", []) if not hasattr(args, "tag") or not args.tag else args.tag
        except Exception as e:
            print(f"Error loading config file: {e}", file=sys.stderr)
            return 1
    else:
        service_id = args.id
        host = args.host
        port = args.port
        protocol = args.protocol or "http"
        tags = args.tag or []

    # Validate required fields
    if not service_id:
        print("Error: --id is required", file=sys.stderr)
        return 1
    if not host:
        print("Error: --host is required", file=sys.stderr)
        return 1
    if port is None:
        print("Error: --port is required", file=sys.stderr)
        return 1

    try:
        result = sync_add_service(args.url, service_id, host, port, protocol, tags)
        if args.json:
            print(format_json(result))
        else:
            print(f"Service '{service_id}' registered successfully.")
            print(format_json(result))
        return 0
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def cmd_unregister(args: argparse.Namespace) -> int:
    """Handle 'unregister' subcommand."""
    if not args.id:
        print("Error: --id is required", file=sys.stderr)
        return 1

    try:
        result = sync_delete_service(args.url, args.id)
        if args.json:
            print(format_json(result))
        else:
            print(result.get("message", "Service deleted."))
        return 0
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def cmd_list(args: argparse.Namespace) -> int:
    """Handle 'list' subcommand."""
    try:
        result = sync_list_services(args.url)
        if args.json:
            print(format_json(result))
        else:
            print(format_table(result))
        return 0
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def cmd_server(args: argparse.Namespace) -> int:
    """Handle 'server' subcommand - start the proxy server."""
    import uvicorn

    uvicorn.run(
        "slim_forwarder.main:app",
        host=args.host,
        port=args.port,
        reload=args.reload,
    )
    return 0


def create_parser() -> argparse.ArgumentParser:
    """Create the argument parser."""
    parser = argparse.ArgumentParser(
        prog="slim-forwarder",
        description="slim-forwarder - A lightweight dynamic web proxy",
    )
    parser.add_argument(
        "--url",
        type=str,
        default="http://localhost:8000",
        help="Base URL of the proxy server (default: http://localhost:8000)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output in JSON format",
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # register command
    register_parser = subparsers.add_parser(
        "register", help="Register a new service"
    )
    register_parser.add_argument(
        "id",
        nargs="?",
        help="Service ID (required unless --config provides it)",
    )
    register_parser.add_argument(
        "--host",
        type=str,
        help="Backend host address (required unless --config provides it)",
    )
    register_parser.add_argument(
        "--port",
        type=int,
        help="Backend port number (required unless --config provides it)",
    )
    register_parser.add_argument(
        "--protocol",
        type=str,
        choices=["http", "https"],
        default="http",
        help="Protocol (http or https, default: http)",
    )
    register_parser.add_argument(
        "--tag",
        action="append",
        help="Tag(s) for the service (can be specified multiple times)",
    )
    register_parser.add_argument(
        "--config",
        type=str,
        help="Path to YAML/JSON config file",
    )
    register_parser.add_argument(
        "--json",
        action="store_true",
        help="Output in JSON format",
    )

    # unregister command
    unregister_parser = subparsers.add_parser(
        "unregister", help="Remove a registered service"
    )
    unregister_parser.add_argument(
        "id",
        help="Service ID to remove",
    )
    unregister_parser.add_argument(
        "--json",
        action="store_true",
        help="Output in JSON format",
    )

    # list command
    list_parser = subparsers.add_parser(
        "list", help="List all registered services"
    )
    list_parser.add_argument(
        "--json",
        action="store_true",
        help="Output in JSON format",
    )

    # server command
    server_parser = subparsers.add_parser(
        "server", help="Start the proxy server"
    )
    server_parser.add_argument(
        "--host",
        type=str,
        default="localhost",
        help="Host to bind to (default: localhost)",
    )
    server_parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port to bind to (default: 8000)",
    )
    server_parser.add_argument(
        "--reload",
        action="store_true",
        help="Enable auto-reload for development",
    )

    return parser


def main() -> int:
    """Main CLI entry point."""
    parser = create_parser()
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 0

    # Map command to handler
    commands = {
        "register": cmd_register,
        "unregister": cmd_unregister,
        "list": cmd_list,
        "server": cmd_server,
    }

    handler = commands.get(args.command)
    if handler:
        return handler(args)

    parser.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())
