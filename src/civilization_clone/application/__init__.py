"""Client-independent application services for game lifecycle and commands."""

from civilization_clone.application.manager import GameManager
from civilization_clone.application.projection import project_event, project_game

__all__ = ["GameManager", "project_event", "project_game"]
