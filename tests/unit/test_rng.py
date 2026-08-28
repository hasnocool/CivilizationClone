# tests/unit/test_rng.py
import pytest

from civilization_clone.engine.rng import DeterministicRng, RngFactory


def test_same_seed_and_stream_produce_same_sequence() -> None:
    first = RngFactory(20260827).stream("map-generation")
    second = RngFactory(20260827).stream("map-generation")

    assert [first.next_u64() for _ in range(20)] == [second.next_u64() for _ in range(20)]


def test_named_streams_are_isolated() -> None:
    factory = RngFactory(42)
    map_rng = factory.stream("map")
    combat_rng = factory.stream("combat")

    assert [map_rng.next_u64() for _ in range(4)] != [combat_rng.next_u64() for _ in range(4)]


def test_restore_replays_from_captured_state() -> None:
    rng = DeterministicRng.from_seed(9)
    _ = [rng.next_u64() for _ in range(3)]
    checkpoint = rng.state
    expected = [rng.next_u64() for _ in range(5)]

    rng.restore(checkpoint)
    assert [rng.next_u64() for _ in range(5)] == expected


def test_randbelow_stays_in_range() -> None:
    rng = DeterministicRng.from_seed(100)
    values = [rng.randbelow(7) for _ in range(500)]

    assert all(0 <= value < 7 for value in values)
    assert len(set(values)) > 1


def test_shuffle_is_reproducible() -> None:
    first = list(range(20))
    second = list(range(20))

    DeterministicRng.from_seed(777).shuffle(first)
    DeterministicRng.from_seed(777).shuffle(second)

    assert first == second
    assert sorted(first) == list(range(20))


def test_invalid_random_requests_raise() -> None:
    rng = DeterministicRng.from_seed(1)

    with pytest.raises(ValueError):
        rng.randbelow(0)
    with pytest.raises(ValueError):
        rng.randint(4, 3)
    with pytest.raises(ValueError):
        rng.choice([])


def test_splitmix64_known_vector_is_stable() -> None:
    rng = DeterministicRng.from_seed(0)

    assert [rng.next_u64() for _ in range(5)] == [
        0xE220A8397B1DCDAF,
        0x6E789E6AA1B965F4,
        0x06C45D188009454F,
        0xF88BB8A8724C81EC,
        0x1B39896A51A8749B,
    ]
