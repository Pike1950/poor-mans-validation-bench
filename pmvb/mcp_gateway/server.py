"""PMVB MCP gateway: Phase 0 scaffold.

Exposes one health-check tool. Real per-module SCPI tools come online with each
module's Phase, registered against this same FastMCP app.

Run directly for local development::

    python -m pmvb.mcp_gateway.server

Default transport is stdio; switch via the FastMCP API or a systemd wrapper
when the gateway moves behind an HTTP front-end.
"""

from __future__ import annotations

import logging
from typing import Any

from mcp.server.fastmcp import FastMCP

from pmvb import __version__

logger = logging.getLogger(__name__)

app = FastMCP("pmvb-gateway")


@app.tool()
def health_check() -> dict[str, Any]:
    """Return a heartbeat from the PMVB MCP gateway.

    Phase 0 placeholder. Always returns status=ok plus gateway identity. Used
    as a smoke test for the MCP plane before any per-module tools register.
    """
    return {
        "status": "ok",
        "gateway": "pmvb-gateway",
        "version": __version__,
        "phase": "0",
    }


def main() -> None:
    """Entrypoint: run the MCP server over the default (stdio) transport."""
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    logger.info("Starting PMVB MCP gateway (Phase 0 scaffold) v%s", __version__)
    app.run()


if __name__ == "__main__":
    main()
