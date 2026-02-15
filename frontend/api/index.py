"""Vercel serverless entry point for the Voice API.

Vercel Python runtime picks up `api/*.py` files and looks for an `app` object.
This adds the frontend directory to sys.path so `voice` and `ingest` packages resolve.
"""

import sys
import os

# The frontend/ directory is the Vercel project root.
# Both `voice/` and `ingest/` live here as sibling packages.
_frontend_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _frontend_root not in sys.path:
    sys.path.insert(0, _frontend_root)

from voice.api.server import app  # noqa: E402, F401
