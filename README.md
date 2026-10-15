# slim-forwarder

A lightweight dynamic web proxy built with FastAPI.

## License

Copyright (C) 2026 Martin Koehler
SPDX-License-Identifier: GPL-3.0-or-later

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

See the [LICENSE](LICENSE) file for details.

## Features

- Proxy HTTP/HTTPS requests to backend services
- Dynamic service registration via REST API
- In-memory storage (no persistence needed)
- Support for both HTTP and HTTPS backends
- Tag-based service organization
- Bulk delete by tag
- CLI tool for easy service management

## Installation

```bash
pip install slim-forwarder
```

Or for development:

```bash
pip install -e .
```

## Usage

### CLI

Start the proxy server:

```bash
# Start server with defaults (localhost:8000)
slim-forwarder server

# Custom host and port
slim-forwarder server --host 0.0.0.0 --port 8080

# Enable auto-reload for development
slim-forwarder server --reload
```

### Module

```bash
python -m slim_forwarder server
```

### Service Management via CLI

Register a service:

```bash
# Register with CLI arguments
slim-forwarder register myapi --host api.example.com --port 443 --protocol https

# Register with multiple tags
slim-forwarder register myapi --host api.example.com --port 443 \
  --tag production --tag api

# Register using YAML config file
cat > config.yaml <<EOF
id: myapi
host: api.example.com
port: 443
protocol: https
tags:
  - production
  - api
EOF

slim-forwarder register --config config.yaml
```

Remove a service:

```bash
slim-forwarder unregister myapi
```

List all services:

```bash
slim-forwarder list
slim-forwarder list --json
```

Delete all services with a tag:

```bash
curl -X DELETE http://localhost:8000/tags/production
```

### API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/health` | Health check |
| `GET` | `/services` | List all configured services (includes tags) |
| `GET` | `/tags` | List all unique tags across services |
| `GET` | `/tags/{tag}` | List services with a specific tag |
| `POST` | `/edit/{service_id}` | Add/update service (body: `{"host": "...", "port": ..., "protocol": "...", "tags": [...]}`) |
| `DELETE` | `/edit/{service_id}` | Remove service |
| `DELETE` | `/tags/{tag}` | Delete all services with given tag |
| `Any` | `/service/{service_id}/{path}` | Proxy to backend |

### Example

```bash
# Add a service with tags
curl -X POST http://localhost:8000/edit/myapi \
  -H "Content-Type: application/json" \
  -d '{
    "host": "api.example.com",
    "port": 443,
    "protocol": "https",
    "tags": ["production", "api"]
  }'

# Proxy a request
curl http://localhost:8000/service/myapi/users

# List services
curl http://localhost:8000/services

# Get all tags
curl http://localhost:8000/tags

# Get services with "production" tag
curl http://localhost:8000/tags/production

# Delete all services with "production" tag
curl -X DELETE http://localhost:8000/tags/production
```

### Environment Variables

- `SLIM_FORWARDER_URL` - Base URL of the proxy server (default: `http://localhost:8000`)
