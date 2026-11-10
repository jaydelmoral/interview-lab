#!/usr/bin/env python3
"""Entry point:  python3 server.py   (see README.md and docs/INSTALL.md for configuration via ILAB_* variables)."""
from pathlib import Path

from interview_lab.web.app import main

if __name__ == "__main__":
    main(Path(__file__).resolve().parent)
