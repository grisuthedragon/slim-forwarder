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

```bash
# Start server with defaults (localhost:8000)
slim-forwarder

# Custom host and port
slim-forwarder --host 0.0.0.0 --port 8080

# Enable auto-reload for development
slim-forwarder --reload
```

### Module

```bash
python -m slim_forwarder
```

### API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/health` | Health check |
| `GET` | `/services` | List all configured services |
| `POST` | `/edit/{service_id}` | Add/update service |
| `DELETE` | `/edit/{service_id}` | Remove service |
| `Any` | `/service/{service_id}/{path}` | Proxy to backend |

### Example

```bash
# Add a service
curl -X POST http://localhost:8000/edit/myapi \
  -H "Content-Type: application/json" \
  -d '{"host": "api.example.com", "port": 443, "protocol": "https"}'

# Proxy a request
curl http://localhost:8000/service/myapi/users

# List services
curl http://localhost:8000/services
```
