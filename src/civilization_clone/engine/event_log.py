"""Deterministic in-memory domain event journal."""

from __future__ import annotations

from collections.abc import Iterable, Iterator
from dataclasses import dataclass, field

from civilization_clone.domain.events import EventEnvelope
from civilization_clone.domain.ids import GameId


class EventLogError(ValueError):
    """Raised when an event violates journal invariants."""


@dataclass(slots=True)
class EventLog:
    """Append-only ordered event journal for exactly one game."""

    game_id: GameId
    _events: list[EventEnvelope] = field(default_factory=list)

    @property
    def next_sequence(self) -> int:
        """Return the next required event sequence number."""
        return len(self._events)

    def append(self, event: EventEnvelope) -> None:
        """Append an event after validating deterministic ordering invariants."""
        if event.game_id != self.game_id:
            raise EventLogError("event game_id does not match journal game_id")
        if event.sequence != self.next_sequence:
            raise EventLogError(
                f"event sequence must be {self.next_sequence}, received {event.sequence}"
            )
        if self._events and event.state_version < self._events[-1].state_version:
            raise EventLogError("event state_version must not move backwards")
        self._events.append(event)

    def extend(self, events: Iterable[EventEnvelope]) -> None:
        """Append events in order, applying the same invariant checks to each."""
        for event in events:
            self.append(event)

    def snapshot(self) -> tuple[EventEnvelope, ...]:
        """Return an immutable snapshot of journal contents."""
        return tuple(self._events)

    def __len__(self) -> int:
        return len(self._events)

    def __iter__(self) -> Iterator[EventEnvelope]:
        return iter(self.snapshot())
