"""Allow running as `python -m slim_forwarder`.

SPDX-License-Identifier: GPL-3.0-or-later
"""

from slim_forwarder.cli import main
import sys

if __name__ == "__main__":
    sys.exit(main())
