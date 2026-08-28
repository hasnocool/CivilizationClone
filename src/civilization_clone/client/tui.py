"""Minimal human-playable terminal client using only public HTTP API contracts."""

from __future__ import annotations

import argparse
import asyncio
import shlex
from dataclasses import dataclass, field
from typing import Any

from civilization_clone.client.http import ApiError, CivilizationApiClient, UrllibJsonTransport

_HELP = """Commands:
  help                              show this help
  actions                           show legal actions and mandatory choices
  events                            show recent authorized events
  switch PLAYER                     switch hotseat viewer
  move UNIT Q R                     move a unit
  attack ATTACKER DEFENDER          attack a visible enemy unit
  found UNIT                        found a settlement
  work SETTLEMENT Q R [on|off]      assign/unassign a worked tile
  produce SETTLEMENT KIND ID        queue unit/building production
  cancel SETTLEMENT [INDEX]         cancel production queue item
  research TECHNOLOGY               select research
  war PLAYER                        declare war
  peace PLAYER                      offer peace
  accept PLAYER                     accept that player's peace offer
  reject PLAYER                     reject that player's peace offer
  trade PLAYER OFFER REQUEST        propose a gold-for-gold trade
  accept-trade PLAYER               accept that player's trade offer
  reject-trade PLAYER               reject that player's trade offer
  cancel-trade PLAYER               withdraw your trade offer to that player
  end                               end the active player's turn
  concede                           concede the current player
  refresh                           redraw current authorized state
  quit                              exit the client
"""


@dataclass(slots=True)
class ClientSession:
    game_id: str
    tokens: dict[str, str] = field(default_factory=dict)
    viewer_id: str = ""

    @property
    def viewer_token(self) -> str:
        token = self.tokens.get(self.viewer_id)
        if token is None:
            raise ValueError("no credential is available for the current viewer")
        return token


async def main_async(base_url: str) -> None:
    api = CivilizationApiClient(UrllibJsonTransport(base_url=base_url))
    await _write(f"CivilizationClone TUI — {base_url}")
    try:
        await api.health()
    except ApiError as exc:
        await _write(f"Cannot reach API: {exc}")
        return

    while True:
        choice = (await _read("[n]ew hotseat game, [a]ttach player, [q]uit > ")).strip().lower()
        if choice in {"q", "quit"}:
            return
        try:
            if choice in {"n", "new"}:
                session = await _new_hotseat(api)
            elif choice in {"a", "attach"}:
                session = await _attach()
            else:
                await _write("Unknown choice.")
                continue
            await _game_loop(api, session)
        except (ApiError, ValueError) as exc:
            await _write(f"Setup failed: {exc}")


async def _new_hotseat(api: CivilizationApiClient) -> ClientSession:
    civilizations = await api.civilizations()
    if not civilizations:
        raise ValueError("server exposes no playable civilizations")
    await _write(render_civilizations(civilizations))
    civilization_ids = {
        str(item.get("civilization_id"))
        for item in civilizations
        if isinstance(item.get("civilization_id"), str)
    }

    game_id = (await _read("Game id [local-game] > ")).strip() or "local-game"
    seed = _parse_int(await _read("Seed [1] > "), 1)
    player_count = _parse_int(await _read("Players 2-4 [2] > "), 2)
    if not 2 <= player_count <= 4:
        raise ValueError("player count must be 2..4")

    created = await api.create_game(game_id, seed=seed, player_count=player_count)
    admin_token = str(created["admin_token"])
    tokens: dict[str, str] = {}
    for index in range(player_count):
        default_id = f"p{index + 1}"
        default_civilization = str(
            civilizations[index % len(civilizations)].get(
                "civilization_id",
                "river_compact",
            )
        )
        player_id = (
            await _read(f"Player {index + 1} id [{default_id}] > ")
        ).strip() or default_id
        name = (
            await _read(f"Player {index + 1} name [{player_id}] > ")
        ).strip() or player_id
        civilization_id = (
            await _read(
                f"Player {index + 1} civilization [{default_civilization}] > "
            )
        ).strip() or default_civilization
        if civilization_id not in civilization_ids:
            raise ValueError(
                f"unknown civilization '{civilization_id}'; choose one listed above"
            )
        joined = await api.join_player(
            game_id,
            admin_token,
            player_id=player_id,
            name=name,
            civilization_id=civilization_id,
        )
        if not joined.get("accepted"):
            raise ValueError(_feedback_text(joined))
        token = joined.get("player_token")
        if not isinstance(token, str):
            raise ValueError("server did not issue a player credential")
        tokens[player_id] = token

    started = await api.start_game(game_id, admin_token)
    if not started.get("accepted"):
        raise ValueError(_feedback_text(started))
    viewer_id = next(iter(tokens))
    await _write(f"Game {game_id} started. Hotseat players: {', '.join(tokens)}")
    return ClientSession(game_id=game_id, tokens=tokens, viewer_id=viewer_id)


async def _attach() -> ClientSession:
    game_id = (await _read("Game id > ")).strip()
    player_id = (await _read("Player id > ")).strip()
    token = (await _read("Player token > ")).strip()
    if not game_id or not player_id or not token:
        raise ValueError("game id, player id, and token are required")
    return ClientSession(game_id=game_id, tokens={player_id: token}, viewer_id=player_id)


async def _game_loop(api: CivilizationApiClient, session: ClientSession) -> None:
    await _write("Type 'help' for commands.")
    while True:
        try:
            state = await api.state(session.game_id, session.viewer_token)
        except ApiError as exc:
            await _write(str(exc))
            return
        await _write(render_state(state))
        if state.get("status") == "finished":
            await _write("Game finished. Use 'events', 'switch', or 'quit'.")

        line = (await _read(f"{session.viewer_id}> ")).strip()
        if not line:
            continue
        try:
            parts = shlex.split(line)
        except ValueError as exc:
            await _write(f"Invalid command line: {exc}")
            continue
        if not parts:
            continue
        verb = parts[0].lower()
        if verb in {"q", "quit", "exit"}:
            return
        if verb in {"h", "help", "?"}:
            await _write(_HELP)
            continue
        if verb in {"refresh", "state"}:
            continue
        if verb == "switch":
            if len(parts) != 2 or parts[1] not in session.tokens:
                await _write(f"Available hotseat players: {', '.join(session.tokens)}")
            else:
                session.viewer_id = parts[1]
            continue
        if verb == "actions":
            try:
                actions = await api.legal_actions(session.game_id, session.viewer_token)
                await _write(render_actions(actions))
            except ApiError as exc:
                await _write(str(exc))
            continue
        if verb == "events":
            try:
                events = await api.events(session.game_id, session.viewer_token)
                await _write(render_events(events[-12:]))
            except ApiError as exc:
                await _write(str(exc))
            continue

        try:
            command_type, payload = parse_player_command(parts)
            result = await api.command(
                session.game_id,
                session.viewer_token,
                command_type,
                player_id=session.viewer_id,
                expected_state_version=int(state["state_version"]),
                payload=payload,
            )
        except (ApiError, ValueError) as exc:
            await _write(f"Command failed: {exc}")
            continue

        if result.get("accepted"):
            event_types = [
                str(event.get("event_type")) for event in result.get("events", [])
            ]
            suffix = f": {', '.join(event_types)}" if event_types else "."
            await _write("Accepted" + suffix)
        else:
            await _write(_feedback_text(result))


def parse_player_command(parts: list[str]) -> tuple[str, dict[str, Any]]:
    """Translate one TUI command into a public API command type/payload."""
    if not parts:
        raise ValueError("command is empty")
    verb = parts[0].lower()
    if verb == "move" and len(parts) == 4:
        return "MoveUnit", {
            "unit_id": parts[1],
            "q": int(parts[2]),
            "r": int(parts[3]),
        }
    if verb == "attack" and len(parts) == 3:
        return "AttackUnit", {"attacker_id": parts[1], "defender_id": parts[2]}
    if verb == "found" and len(parts) == 2:
        return "FoundSettlement", {"unit_id": parts[1]}
    if verb == "work" and len(parts) in {4, 5}:
        worked = True if len(parts) == 4 else parts[4].lower() not in {
            "off",
            "false",
            "0",
            "no",
        }
        return "SetWorkedTile", {
            "settlement_id": parts[1],
            "q": int(parts[2]),
            "r": int(parts[3]),
            "worked": worked,
        }
    if verb == "produce" and len(parts) == 4:
        return "QueueProduction", {
            "settlement_id": parts[1],
            "kind": parts[2],
            "definition_id": parts[3],
        }
    if verb == "cancel" and len(parts) in {2, 3}:
        return "CancelProduction", {
            "settlement_id": parts[1],
            "index": 0 if len(parts) == 2 else int(parts[2]),
        }
    if verb == "research" and len(parts) == 2:
        return "ChooseResearch", {"technology_id": parts[1]}
    if verb == "war" and len(parts) == 2:
        return "DeclareWar", {"target_player_id": parts[1]}
    if verb == "peace" and len(parts) == 2:
        return "OfferPeace", {"target_player_id": parts[1]}
    if verb == "accept" and len(parts) == 2:
        return "AcceptPeace", {"target_player_id": parts[1]}
    if verb == "reject" and len(parts) == 2:
        return "RejectPeace", {"target_player_id": parts[1]}
    if verb == "trade" and len(parts) == 4:
        return "OfferTrade", {
            "target_player_id": parts[1],
            "offered_gold": int(parts[2]),
            "requested_gold": int(parts[3]),
        }
    if verb == "accept-trade" and len(parts) == 2:
        return "AcceptTrade", {"target_player_id": parts[1]}
    if verb == "reject-trade" and len(parts) == 2:
        return "RejectTrade", {"target_player_id": parts[1]}
    if verb == "cancel-trade" and len(parts) == 2:
        return "CancelTrade", {"target_player_id": parts[1]}
    if verb in {"end", "endturn"} and len(parts) == 1:
        return "EndTurn", {}
    if verb == "concede" and len(parts) == 1:
        return "Concede", {}
    raise ValueError("unknown command or wrong arguments; type 'help'")


def render_civilizations(civilizations: list[dict[str, Any]]) -> str:
    """Render public civilization content and gameplay bonuses returned by the API."""
    lines = ["Available civilizations:"]
    for item in civilizations:
        civilization_id = item.get("civilization_id", "?")
        name = item.get("name", civilization_id)
        description = item.get("description", "")
        tags = ", ".join(str(tag) for tag in item.get("tags", []))
        lines.append(f"  {civilization_id}: {name} [{tags}]")
        if description:
            lines.append(f"    {description}")
        bonuses = _civilization_bonus_text(item)
        if bonuses:
            lines.append(f"    Bonuses: {bonuses}")
    return "\n".join(lines)


def _civilization_bonus_text(item: dict[str, Any]) -> str:
    bonuses: list[str] = []
    resources = _mapping(item.get("starting_resources", {}))
    if resources:
        bonuses.append(
            "start "
            + ", ".join(
                f"{key} +{value}" for key, value in sorted(resources.items())
            )
        )
    for raw_modifier in item.get("yield_modifiers", []):
        modifier = _mapping(raw_modifier)
        operation = str(modifier.get("operation", ""))
        value = modifier.get("value", 0)
        yield_type = modifier.get("yield_type", "yield")
        if operation == "flat":
            bonuses.append(f"{yield_type} {int(value):+d} per settlement")
        elif operation == "percent":
            bonuses.append(f"{yield_type} {int(value):+d}% per settlement")
    for field_name, label in (
        ("research_cost_percent", "research cost"),
        ("attack_strength_percent", "attack strength"),
        ("defense_strength_percent", "defense strength"),
    ):
        value = item.get(field_name, 0)
        if isinstance(value, int) and not isinstance(value, bool) and value != 0:
            bonuses.append(f"{label} {value:+d}%")
    return "; ".join(bonuses)


def render_state(state: dict[str, Any]) -> str:
    """Render one authorized player projection as compact terminal text."""
    viewer = _mapping(state.get("viewer", {}))
    research = _mapping(viewer.get("research", {}))
    lines = [
        "=" * 72,
        f"Game {state.get('game_id')} | turn {state.get('turn')} | {state.get('status')} | "
        f"active={state.get('active_player_id')} | viewer={viewer.get('player_id')} | "
        f"civ={viewer.get('civilization_id', '-')}",
        f"Gold {viewer.get('gold', 0)}  Science {viewer.get('science', 0)}  "
        f"Culture {viewer.get('culture', 0)}  Research {research.get('selected') or '-'}",
        render_map(state),
    ]
    units = [_mapping(item) for item in state.get("units", [])]
    if units:
        lines.append(
            "Units: "
            + "; ".join(
                f"{unit.get('unit_id')}:{unit.get('definition_id')}@"
                f"({unit.get('q')},{unit.get('r')}) hp={unit.get('hit_points')} "
                f"mv={unit.get('movement_remaining')} owner={unit.get('owner_id')}"
                for unit in units
            )
        )
    settlements = [_mapping(item) for item in state.get("settlements", [])]
    if settlements:
        lines.append(
            "Settlements: "
            + "; ".join(
                f"{item.get('settlement_id')}@({item.get('q')},{item.get('r')}) "
                f"pop={item.get('population')} owner={item.get('owner_id')}"
                for item in settlements
            )
        )
    diplomacy = [_mapping(item) for item in state.get("diplomacy", [])]
    if diplomacy:
        lines.append("Diplomacy: " + "; ".join(_diplomacy_text(item) for item in diplomacy))
    victory = state.get("victory")
    if isinstance(victory, dict):
        lines.append(
            f"VICTORY: {victory.get('winner_id')} by {victory.get('victory_type')} "
            f"score={victory.get('score')}"
        )
    return "\n".join(lines)


def _diplomacy_text(relation: dict[str, Any]) -> str:
    text = f"{relation.get('other_player_id')}={relation.get('status')}"
    pending = relation.get("pending_trade")
    if isinstance(pending, dict):
        text += (
            f" trade[{pending.get('proposer_id')} offers {pending.get('offered_gold', 0)}g "
            f"for {pending.get('requested_gold', 0)}g]"
        )
    completed = int(relation.get("completed_trades", 0))
    if completed:
        text += f" completed={completed}"
    return text


def render_map(state: dict[str, Any]) -> str:
    map_data = _mapping(state.get("map", {}))
    radius = int(map_data.get("radius", 0))
    tiles = {
        (int(tile["q"]), int(tile["r"])): _mapping(tile)
        for raw in map_data.get("tiles", [])
        if isinstance(raw, dict)
        for tile in [raw]
    }
    overlay: dict[tuple[int, int], str] = {}
    viewer_id = str(_mapping(state.get("viewer", {})).get("player_id", ""))
    for raw in state.get("settlements", []):
        item = _mapping(raw)
        marker = "S" if item.get("owner_id") == viewer_id else "s"
        overlay[(int(item["q"]), int(item["r"]))] = marker
    for raw in state.get("units", []):
        item = _mapping(raw)
        marker = "U" if item.get("owner_id") == viewer_id else "e"
        overlay[(int(item["q"]), int(item["r"]))] = marker

    symbols = {
        "water": "~",
        "plains": ".",
        "grassland": ",",
        "hills": "^",
        "desert": ":",
        "tundra": "*",
    }
    lines = ["Map: U=you e=enemy S=your settlement s=enemy  ~=water ^=hills"]
    for r in range(-radius, radius + 1):
        cells: list[str] = []
        for q in range(-radius, radius + 1):
            tile = tiles.get((q, r))
            if tile is None:
                cells.append(" ")
                continue
            symbol = overlay.get((q, r), symbols.get(str(tile.get("terrain")), "?"))
            if tile.get("visibility") == "discovered" and (q, r) not in overlay:
                symbol = symbol.lower()
            cells.append(symbol)
        lines.append(" " * max(0, radius - r) + " ".join(cells))
    return "\n".join(lines)


def render_actions(actions: dict[str, Any]) -> str:
    lines = [
        f"Active player: {actions.get('is_active_player')}",
        "Actions: " + ", ".join(str(item) for item in actions.get("actions", [])),
    ]
    mandatory = actions.get("mandatory_decisions", [])
    if mandatory:
        lines.append("Mandatory: " + repr(mandatory))
    return "\n".join(lines)


def render_events(events: list[dict[str, Any]]) -> str:
    if not events:
        return "No authorized events."
    return "\n".join(
        f"#{event.get('sequence')} {event.get('event_type')} {event.get('payload', {})}"
        for event in events
    )


def _feedback_text(result: dict[str, Any]) -> str:
    feedback = result.get("feedback", [])
    if not isinstance(feedback, list) or not feedback:
        return "Command rejected."
    return " | ".join(
        f"{item.get('code', 'ERROR')}: {item.get('message', '')}"
        for item in feedback
        if isinstance(item, dict)
    )


def _parse_int(raw: str, default: int) -> int:
    stripped = raw.strip()
    return default if not stripped else int(stripped)


def _mapping(value: Any) -> dict[str, Any]:
    return dict(value) if isinstance(value, dict) else {}


async def _read(prompt: str) -> str:
    return await asyncio.to_thread(input, prompt)


async def _write(text: str) -> None:
    await asyncio.to_thread(print, text)


def main() -> None:
    parser = argparse.ArgumentParser(description="Play CivilizationClone through its public API")
    parser.add_argument(
        "--url",
        default="http://127.0.0.1:8000",
        help="CivilizationClone API base URL",
    )
    args = parser.parse_args()
    try:
        asyncio.run(main_async(args.url))
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
