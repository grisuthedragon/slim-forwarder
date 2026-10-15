"""slim-forwarder - A lightweight dynamic web proxy.

Copyright (C) 2026 Martin Koehler
This program comes with ABSOLUTELY NO WARRANTY.
This is free software, and you are welcome to redistribute it
under certain conditions; see LICENSE for details.
SPDX-License-Identifier: GPL-3.0-or-later
"""

from .main import app
from .services import Service, ServiceRegistry, registry

__all__ = ["app", "Service", "ServiceRegistry", "registry"]
