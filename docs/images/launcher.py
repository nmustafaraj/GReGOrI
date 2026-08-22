#!/usr/bin/env python3
"""GReGOrI Launcher: starts the local Web Interface."""
from __future__ import annotations

import sys
from pathlib import Path

# Ensure root is on python path
ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from gregori.server.app import main

if __name__ == "__main__":
    main()
