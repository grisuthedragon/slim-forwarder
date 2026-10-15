"""In-memory service registry for dynamic proxy.

SPDX-License-Identifier: GPL-3.0-or-later
"""

from dataclasses import dataclass
from typing import Dict, Optional


@dataclass
class Service:
    """Represents a backend service configuration."""
    id: str
    host: str
    port: int
    protocol: str = "http"


class ServiceRegistry:
    """Thread-safe in-memory storage for services."""

    def __init__(self):
        self._services: Dict[str, Service] = {}

    def add_service(self, id: str, host: str, port: int, protocol: str = "http") -> Service:
        """Add or update a service."""
        service = Service(id=id, host=host, port=port, protocol=protocol)
        self._services[id] = service
        return service

    def get_service(self, id: str) -> Optional[Service]:
        """Get a service by ID."""
        return self._services.get(id)

    def delete_service(self, id: str) -> bool:
        """Delete a service by ID. Returns True if found and deleted."""
        if id in self._services:
            del self._services[id]
            return True
        return False

    def list_services(self) -> Dict[str, Service]:
        """Return all services."""
        return self._services.copy()


# Global registry instance
registry = ServiceRegistry()
