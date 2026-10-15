"""Tests for the services module.

SPDX-License-Identifier: GPL-3.0-or-later
"""

import pytest

from slim_forwarder import Service, ServiceRegistry


class TestService:
    """Tests for the Service dataclass."""

    def test_service_creation(self):
        """Test creating a Service instance."""
        service = Service(id="test", host="example.com", port=80)
        assert service.id == "test"
        assert service.host == "example.com"
        assert service.port == 80
        assert service.protocol == "http"  # Default value

    def test_service_with_protocol(self):
        """Test creating a Service with custom protocol."""
        service = Service(id="test", host="example.com", port=443, protocol="https")
        assert service.protocol == "https"

    def test_service_with_tags(self):
        """Test creating a Service with tags."""
        service = Service(id="test", host="example.com", port=80, tags=["production", "api"])
        assert service.tags == ["production", "api"]

    def test_service_default_tags(self):
        """Test that Service has empty tags list by default."""
        service = Service(id="test", host="example.com", port=80)
        assert service.tags == []


class TestServiceRegistry:
    """Tests for the ServiceRegistry class."""

    def setup_method(self):
        """Create a fresh registry for each test."""
        self.registry = ServiceRegistry()

    def test_add_service(self):
        """Test adding a service."""
        service = self.registry.add_service("test", "example.com", 80)
        assert service.id == "test"
        assert service.host == "example.com"
        assert service.port == 80

    def test_add_service_with_protocol(self):
        """Test adding a service with custom protocol."""
        service = self.registry.add_service("test", "example.com", 443, "https")
        assert service.protocol == "https"

    def test_get_service_exists(self):
        """Test getting an existing service."""
        self.registry.add_service("test", "example.com", 80)
        service = self.registry.get_service("test")
        assert service is not None
        assert service.id == "test"

    def test_get_service_not_exists(self):
        """Test getting a non-existing service."""
        service = self.registry.get_service("nonexistent")
        assert service is None

    def test_delete_service_exists(self):
        """Test deleting an existing service."""
        self.registry.add_service("test", "example.com", 80)
        result = self.registry.delete_service("test")
        assert result is True
        assert self.registry.get_service("test") is None

    def test_delete_service_not_exists(self):
        """Test deleting a non-existing service."""
        result = self.registry.delete_service("nonexistent")
        assert result is False

    def test_list_services(self):
        """Test listing services."""
        self.registry.add_service("service1", "example.com", 80)
        self.registry.add_service("service2", "example.com", 443)
        services = self.registry.list_services()
        assert len(services) == 2
        assert "service1" in services
        assert "service2" in services

    def test_list_services_is_copy(self):
        """Test that list_services returns a copy, not the original."""
        self.registry.add_service("test", "example.com", 80)
        services = self.registry.list_services()
        services["new"] = Service("new", "other.com", 80)
        # Original should not be modified
        assert len(self.registry.list_services()) == 1

    def test_update_service(self):
        """Test updating an existing service."""
        self.registry.add_service("test", "example.com", 80)
        service = self.registry.add_service("test", "newhost.com", 8080)
        assert service.host == "newhost.com"
        assert service.port == 8080
        assert self.registry.get_service("test").host == "newhost.com"

    def test_add_service_with_tags(self):
        """Test adding a service with tags."""
        service = self.registry.add_service("test", "example.com", 80, tags=["production"])
        assert service.tags == ["production"]

    def test_delete_services_by_tag(self):
        """Test deleting services by tag."""
        self.registry.add_service("service1", "example.com", 80, tags=["production", "api"])
        self.registry.add_service("service2", "example.com", 443, tags=["production"])
        self.registry.add_service("service3", "example.com", 8080, tags=["staging"])

        deleted = self.registry.delete_services_by_tag("production")
        assert len(deleted) == 2
        assert "service1" in deleted
        assert "service2" in deleted
        assert self.registry.get_service("service3") is not None
        assert self.registry.get_service("service1") is None
        assert self.registry.get_service("service2") is None

    def test_delete_services_by_tag_none_found(self):
        """Test deleting services by tag when none found."""
        self.registry.add_service("test", "example.com", 80, tags=["production"])
        deleted = self.registry.delete_services_by_tag("nonexistent")
        assert deleted == []

    def test_get_all_tags(self):
        """Test getting all unique tags."""
        self.registry.add_service("service1", "example.com", 80, tags=["production", "api"])
        self.registry.add_service("service2", "example.com", 443, tags=["production", "staging"])
        self.registry.add_service("service3", "example.com", 8080, tags=["development"])

        tags = self.registry.get_all_tags()
        assert len(tags) == 4
        assert "production" in tags
        assert "api" in tags
        assert "staging" in tags
        assert "development" in tags

    def test_get_all_tags_empty(self):
        """Test getting all tags when no services have tags."""
        self.registry.add_service("test", "example.com", 80)
        tags = self.registry.get_all_tags()
        assert tags == []

    def test_get_services_by_tag(self):
        """Test getting services by tag."""
        self.registry.add_service("service1", "example.com", 80, tags=["production", "api"])
        self.registry.add_service("service2", "example.com", 443, tags=["production"])
        self.registry.add_service("service3", "example.com", 8080, tags=["staging"])

        services = self.registry.get_services_by_tag("production")
        assert len(services) == 2
        assert services[0].id == "service1"
        assert services[1].id == "service2"

    def test_get_services_by_tag_none_found(self):
        """Test getting services by tag when none found."""
        self.registry.add_service("test", "example.com", 80, tags=["production"])
        services = self.registry.get_services_by_tag("nonexistent")
        assert services == []
