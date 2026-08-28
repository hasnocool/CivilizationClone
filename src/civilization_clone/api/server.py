"""Runnable persistent FastAPI server configuration."""

from __future__ import annotations

import os
from pathlib import Path

import uvicorn

from civilization_clone.api.app import create_app
from civilization_clone.application.manager import GameManager
from civilization_clone.persistence.sqlite_store import SqliteGameStore


def build_app():
    """Build the default server using durable SQLite persistence."""
    database_path = Path(
        os.environ.get("CIVILIZATION_CLONE_DB", "data/civilization_clone.sqlite3")
    )
    return create_app(GameManager(store=SqliteGameStore(database_path)))


app = build_app()


def main() -> None:
    """Run the local API server."""
    host = os.environ.get("CIVILIZATION_CLONE_HOST", "127.0.0.1")
    raw_port = os.environ.get("CIVILIZATION_CLONE_PORT", "8000")
    try:
        port = int(raw_port)
    except ValueError as exc:
        raise SystemExit("CIVILIZATION_CLONE_PORT must be an integer") from exc
    if not 1 <= port <= 65535:
        raise SystemExit("CIVILIZATION_CLONE_PORT must be between 1 and 65535")
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    main()
