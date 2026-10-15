"""FastAPI application for dynamic web proxy.

Copyright (C) 2026 Martin Koehler
SPDX-License-Identifier: GPL-3.0-or-later
"""

import asyncio
import httpx
from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse
from urllib.parse import urlparse

from .services import registry
from typing import List


def create_proxy_endpoint():
    """Create a proxy endpoint function that can be used with Starlette routes."""

    async def proxy_endpoint(request: Request) -> Response:
        """Proxy request to the target service."""
        # The path is /service/<service_id>/<rest>
        # We need to extract service_id as the first segment after /service/
        path = request.url.path
        if not path.startswith('/service/'):
            return Response(status_code=404, content="Invalid path")

        # Split path: /service/test1/get -> ['', 'service', 'test1', 'get']
        parts = path.split('/')
        if len(parts) < 3:
            return Response(status_code=404, content="Service ID required")

        service_id = parts[2]  # Third element after splitting
        # The remaining path is everything after /service/{service_id}/
        remaining_path = '/' + '/'.join(parts[3:]) if len(parts) > 3 else '/'

        service = registry.get_service(service_id)
        if not service:
            return Response(status_code=404, content=f"Service '{service_id}' not found")

        # Build target URL from service config, preserving the remaining path
        protocol = service.protocol or "http"
        target_url = f"{protocol}://{service.host}:{service.port}{remaining_path}"

        # Get request body
        body = await request.body()

        # Forward headers (filtering out hop-by-hop headers)
        forward_headers = {
            k: v for k, v in request.headers.items()
            if k.lower() not in ('host', 'transfer-encoding', 'connection')
        }
        forward_headers['x-forwarded-host'] = request.headers.get('host', '')
        forward_headers['x-forwarded-proto'] = protocol

        async with httpx.AsyncClient() as client:
            try:
                response = await client.request(
                    method=request.method,
                    url=target_url,
                    headers=forward_headers,
                    content=body,
                    follow_redirects=True,
                    timeout=30.0,
                )
                return Response(
                    content=response.content,
                    status_code=response.status_code,
                    headers=dict(response.headers),
                )
            except httpx.RequestError as e:
                return Response(
                    status_code=502,
                    content=f"Error forwarding to service: {str(e)}"
                )

    return proxy_endpoint


app = FastAPI(title="Dynamic Web Proxy")


@app.post("/edit/{service_id}")
async def add_service(service_id: str, request: Request) -> JSONResponse:
    """
    Add or update a service configuration.
    Body: {"host": "string", "port": integer, "protocol": "http"|"https", "tags": ["tag1", "tag2"]}
    """
    try:
        data = await request.json()
        host = data.get("host")
        port = data.get("port")
        protocol = data.get("protocol", "http")
        tags = data.get("tags", [])

        if not host or port is None:
            return JSONResponse(
                status_code=400,
                content={"error": "Missing 'host' or 'port' in request body"}
            )

        if protocol not in ("http", "https"):
            return JSONResponse(
                status_code=400,
                content={"error": "Protocol must be 'http' or 'https'"}
            )

        service = registry.add_service(
            id=service_id, host=host, port=int(port), protocol=protocol, tags=tags
        )
        return JSONResponse(
            status_code=201,
            content={
                "id": service.id,
                "host": service.host,
                "port": service.port,
                "protocol": service.protocol,
                "tags": service.tags,
            },
        )
    except Exception as e:
        return JSONResponse(status_code=400, content={"error": str(e)})


@app.delete("/edit/{service_id}")
async def delete_service(service_id: str) -> JSONResponse:
    """
    Delete a service configuration.
    """
    if registry.delete_service(service_id):
        return JSONResponse(status_code=200, content={"message": f"Service '{service_id}' deleted"})
    return JSONResponse(status_code=404, content={"error": f"Service '{service_id}' not found"})


@app.get("/tags")
async def get_all_tags() -> JSONResponse:
    """
    Get all unique tags across all services.
    """
    tags = registry.get_all_tags()
    return JSONResponse(status_code=200, content=tags)


@app.get("/tags/{tag}")
async def get_services_by_tag(tag: str) -> JSONResponse:
    """
    Get all services with a given tag.
    """
    services = registry.get_services_by_tag(tag)
    if services:
        return JSONResponse(
            status_code=200,
            content=[
                {"id": s.id, "host": s.host, "port": s.port, "protocol": s.protocol, "tags": s.tags}
                for s in services
            ],
        )
    return JSONResponse(status_code=404, content={"error": f"No services found with tag '{tag}'"})


@app.delete("/tags/{tag}")
async def delete_services_by_tag(tag: str) -> JSONResponse:
    """
    Delete all services with a given tag.
    """
    deleted = registry.delete_services_by_tag(tag)
    if deleted:
        return JSONResponse(
            status_code=200,
            content={"deleted": deleted, "count": len(deleted)},
        )
    return JSONResponse(status_code=404, content={"error": f"No services found with tag '{tag}'"})


@app.get("/health")
async def health_check() -> JSONResponse:
    """Health check endpoint."""
    return JSONResponse(status_code=200, content={"status": "ok"})


@app.get("/services")
async def list_services() -> JSONResponse:
    """List all configured services."""
    services = registry.list_services()
    return JSONResponse(
        status_code=200,
        content={
            sid: {"host": s.host, "port": s.port, "protocol": s.protocol, "tags": s.tags}
            for sid, s in services.items()
        },
    )


# Proxy routes - registered last to not override other routes
PROXY_METHODS = ["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"]

app.add_route(
    "/service/{service_id:path}",
    create_proxy_endpoint(),
    methods=PROXY_METHODS,
)
