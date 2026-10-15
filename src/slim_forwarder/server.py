"""Standalone entry point that starts the proxy server.

SPDX-License-Identifier: GPL-3.0-or-later
"""

import argparse


def run(host: str, port: int, reload: bool = False) -> None:
    """Start the FastAPI proxy under uvicorn."""
    import uvicorn

    uvicorn.run(
        "slim_forwarder.main:app",
        host=host,
        port=port,
        reload=reload,
    )


def create_parser() -> argparse.ArgumentParser:
    """Create the argument parser for the standalone server command."""
    parser = argparse.ArgumentParser(
        prog="slim-forwarder-server",
        description="Start the slim-forwarder proxy server",
    )
    parser.add_argument(
        "--host",
        type=str,
        default="localhost",
        help="Host to bind to (default: localhost)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port to bind to (default: 8000)",
    )
    parser.add_argument(
        "--reload",
        action="store_true",
        help="Enable auto-reload for development",
    )
    return parser


def main() -> int:
    """Main entry point for the standalone server command."""
    args = create_parser().parse_args()
    run(args.host, args.port, args.reload)
    return 0


if __name__ == "__main__":
    import sys

    sys.exit(main())
