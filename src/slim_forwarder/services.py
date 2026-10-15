"""In-memory service registry for dynamic proxy.

SPDX-License-Identifier: GPL-3.0-or-later
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class Service:
    """Represents a backend service configuration."""
    id: str
    host: str
    port: int
    protocol: str = "http"
    tags: List[str] = field(default_factory=list)


class ServiceRegistry:
    """Thread-safe in-memory storage for services."""

    def __init__(self):
        self._services: Dict[str, Service] = {}

    def add_service(
        self, id: str, host: str, port: int, protocol: str = "http", tags: List[str] = None
    ) -> Service:
        """Add or update a service."""
        service = Service(id=id, host=host, port=port, protocol=protocol, tags=tags or [])
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

    def delete_services_by_tag(self, tag: str) -> List[str]:
        """Delete all services with a given tag. Returns list of deleted service IDs."""
        deleted = []
        for service_id in list(self._services.keys()):
            if tag in self._services[service_id].tags:
                del self._services[service_id]
                deleted.append(service_id)
        return deleted


# Global registry instance
registry = ServiceRegistry()
