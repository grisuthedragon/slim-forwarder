"""HTTP API client for slim-forwarder service management.

SPDX-License-Identifier: GPL-3.0-or-later
"""

import os
from typing import Dict, List, Optional

import httpx


class APIClient:
    """Client for the slim-forwarder HTTP API."""

    def __init__(self, base_url: Optional[str] = None):
        """Initialize the API client.

        Args:
            base_url: Base URL of the proxy server. Defaults to
                     environment variable SLIM_FORWARDER_URL or http://localhost:8000
        """
        self.base_url = base_url or os.environ.get(
            "SLIM_FORWARDER_URL",
            "http://localhost:8000"
        ).rstrip("/")
        self.client = httpx.AsyncClient(base_url=self.base_url, timeout=30.0)

    async def add_service(
        self,
        service_id: str,
        host: str,
        port: int,
        protocol: str = "http"
    ) -> Dict:
        """Register a new service.

        Args:
            service_id: Unique identifier for the service
            host: Backend host address
            port: Backend port number
            protocol: Protocol (http or https)

        Returns:
            Service configuration as dict
        """
        response = await self.client.post(
            f"/edit/{service_id}",
            json={"host": host, "port": port, "protocol": protocol}
        )
        response.raise_for_status()
        return response.json()

    async def delete_service(self, service_id: str) -> Dict:
        """Remove a service.

        Args:
            service_id: Unique identifier for the service

        Returns:
            Response message as dict
        """
        response = await self.client.delete(f"/edit/{service_id}")
        response.raise_for_status()
        return response.json()

    async def list_services(self) -> Dict:
        """List all registered services.

        Returns:
            Dict mapping service IDs to their configurations
        """
        response = await self.client.get("/services")
        response.raise_for_status()
        return response.json()

    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()


def sync_add_service(
    base_url: str,
    service_id: str,
    host: str,
    port: int,
    protocol: str = "http",
    tags: List[str] = None,
) -> Dict:
    """Synchronously register a service.

    Args:
        base_url: Base URL of the proxy server
        service_id: Unique identifier for the service
        host: Backend host address
        port: Backend port number
        protocol: Protocol (http or https)
        tags: List of tags for the service

    Returns:
        Service configuration as dict
    """
    payload = {"host": host, "port": port, "protocol": protocol}
    if tags:
        payload["tags"] = tags

    with httpx.Client(base_url=base_url, timeout=30.0) as client:
        response = client.post(f"/edit/{service_id}", json=payload)
        response.raise_for_status()
        return response.json()


def sync_delete_service(base_url: str, service_id: str) -> Dict:
    """Synchronously remove a service.

    Args:
        base_url: Base URL of the proxy server
        service_id: Unique identifier for the service

    Returns:
        Response message as dict
    """
    with httpx.Client(base_url=base_url, timeout=30.0) as client:
        response = client.delete(f"/edit/{service_id}")
        response.raise_for_status()
        return response.json()


def sync_list_services(base_url: str) -> Dict:
    """Synchronously list all services.

    Args:
        base_url: Base URL of the proxy server

    Returns:
        Dict mapping service IDs to their configurations
    """
    with httpx.Client(base_url=base_url, timeout=30.0) as client:
        response = client.get("/services")
        response.raise_for_status()
        return response.json()
