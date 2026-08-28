"""Stable seeded pseudo-random number generation for deterministic simulation."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from hashlib import blake2b

_MASK_64 = (1 << 64) - 1
_GOLDEN_GAMMA = 0x9E3779B97F4A7C15


def _mix64(value: int) -> int:
    value = (value ^ (value >> 30)) * 0xBF58476D1CE4E5B9 & _MASK_64
    value = (value ^ (value >> 27)) * 0x94D049BB133111EB & _MASK_64
    return (value ^ (value >> 31)) & _MASK_64


def _derive_seed(root_seed: int, stream: str) -> int:
    if not stream:
        raise ValueError("stream name must not be empty")
    seed_bytes = (root_seed & _MASK_64).to_bytes(8, "big", signed=False)
    digest = blake2b(seed_bytes + b"\0" + stream.encode("utf-8"), digest_size=8).digest()
    return int.from_bytes(digest, "big", signed=False)


@dataclass(slots=True)
class DeterministicRng:
    """SplitMix64 stream with explicit, serializable state.

    This implementation avoids Python's module-level ``random`` state so engine results are isolated
    from unrelated code and reproducible from the same stream state.
    """

    _state: int

    @classmethod
    def from_seed(cls, seed: int) -> "DeterministicRng":
        return cls(seed & _MASK_64)

    @property
    def state(self) -> int:
        """Return the exact serializable stream state."""
        return self._state

    def restore(self, state: int) -> None:
        """Restore a previously captured stream state."""
        self._state = state & _MASK_64

    def next_u64(self) -> int:
        """Return the next unsigned 64-bit value."""
        self._state = (self._state + _GOLDEN_GAMMA) & _MASK_64
        return _mix64(self._state)

    def random(self) -> float:
        """Return a deterministic float in the half-open interval [0.0, 1.0)."""
        return (self.next_u64() >> 11) * (1.0 / (1 << 53))

    def randbelow(self, upper_bound: int) -> int:
        """Return an unbiased integer in ``range(upper_bound)``."""
        if upper_bound <= 0:
            raise ValueError("upper_bound must be positive")
        if upper_bound > 1 << 64:
            raise ValueError("upper_bound must not exceed 2**64")

        limit = (1 << 64) - ((1 << 64) % upper_bound)
        while True:
            candidate = self.next_u64()
            if candidate < limit:
                return candidate % upper_bound

    def randint(self, lower_bound: int, upper_bound: int) -> int:
        """Return an integer in the inclusive interval [lower_bound, upper_bound]."""
        if lower_bound > upper_bound:
            raise ValueError("lower_bound must not exceed upper_bound")
        width = upper_bound - lower_bound + 1
        if width > 1 << 64:
            raise ValueError("requested interval is too large")
        return lower_bound + self.randbelow(width)

    def choice[T](self, values: Sequence[T]) -> T:
        """Choose one item from a non-empty sequence."""
        if not values:
            raise ValueError("cannot choose from an empty sequence")
        return values[self.randbelow(len(values))]

    def shuffle[T](self, values: list[T]) -> None:
        """Shuffle a list in place using deterministic Fisher-Yates ordering."""
        for index in range(len(values) - 1, 0, -1):
            swap_index = self.randbelow(index + 1)
            values[index], values[swap_index] = values[swap_index], values[index]


@dataclass(frozen=True, slots=True)
class RngFactory:
    """Creates isolated deterministic streams from one game seed."""

    root_seed: int

    def stream(self, name: str) -> DeterministicRng:
        return DeterministicRng.from_seed(_derive_seed(self.root_seed, name))
