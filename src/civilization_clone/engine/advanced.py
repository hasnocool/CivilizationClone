"""Post-POC command extensions layered over the deterministic core engine.

The base ``GameEngine`` remains the v1.0 command processor. ``AdvancedGameEngine``
extends it with v1.1 diplomacy/trade commands while preserving the same command
idempotency, stale-version, event-journal, and safe-feedback semantics.
"""

from __future__ import annotations

from civilization_clone.domain.events import EventEnvelope
from civilization_clone.domain.ids import CommandId, PlayerId
from civilization_clone.domain.strategy import TradeOffer
from civilization_clone.domain.types import JsonValue
from civilization_clone.engine.commands import CommandEnvelope
from civilization_clone.engine.diplomacy import (
    accept_trade,
    cancel_trade,
    cancel_trade_offers_for_player,
    offer_trade,
    reject_trade,
)
from civilization_clone.engine.session import CommandResult, GameEngine

_TRADE_COMMANDS = frozenset({"OfferTrade", "AcceptTrade", "RejectTrade", "CancelTrade"})


class AdvancedGameEngine(GameEngine):
    """v1.1 engine with deterministic bilateral trade command support."""

    def process(self, command: CommandEnvelope) -> CommandResult:
        """Process v1.1 commands or delegate unchanged v1.0 commands to the base engine."""
        if command.command_type not in _TRADE_COMMANDS:
            return super().process(command)
        if command.game_id != self.session.game_id:
            return self._rejected("WRONG_GAME", "Command targets a different game.")
        cached = self._processed.get(command.command_id)
        if cached is not None:
            return cached
        if (
            command.expected_state_version is not None
            and command.expected_state_version != self.session.state_version
        ):
            result = self._rejected(
                "STALE_STATE_VERSION",
                "The game changed before this command could be applied.",
                {"current_state_version": str(self.session.state_version)},
            )
            self._processed[command.command_id] = result
            return result

        handlers = {
            "OfferTrade": self._offer_trade,
            "AcceptTrade": self._accept_trade,
            "RejectTrade": self._reject_trade,
            "CancelTrade": self._cancel_trade,
        }
        result = handlers[command.command_type](command)
        if not result.accepted:
            error_code = result.feedback[0].code if result.feedback else "COMMAND_REJECTED"
            self._log(command, "command rejected", error_code=error_code)
        self._processed[command.command_id] = result
        return result

    def _offer_trade(self, command: CommandEnvelope) -> CommandResult:
        player_id = self._active_player(command)
        target = self._target_player(command)
        if player_id is None:
            return self._rejected("NOT_ACTIVE_PLAYER", "Only the active player may offer trade.")
        if target is None:
            return self._rejected("INVALID_TRADE", "target_player_id is required.")
        offered_gold = self._trade_amount(command, "offered_gold")
        requested_gold = self._trade_amount(command, "requested_gold")
        if offered_gold is None or requested_gold is None:
            return self._rejected(
                "INVALID_TRADE",
                "offered_gold and requested_gold must be non-negative integers.",
            )
        reason = offer_trade(self.session, player_id, target, offered_gold, requested_gold)
        if reason is not None:
            return self._rejected(
                "TRADE_REJECTED",
                "That trade offer is not allowed.",
                {"reason": reason},
            )
        self.session.state_version += 1
        event = self._emit(
            "TradeOffered",
            {
                "player_id": player_id,
                "target_player_id": target,
                "offered_gold": offered_gold,
                "requested_gold": requested_gold,
            },
            command.command_id,
        )
        return CommandResult(True, self.session.state_version, (event,))

    def _accept_trade(self, command: CommandEnvelope) -> CommandResult:
        player_id = self._active_player(command)
        target = self._target_player(command)
        if player_id is None:
            return self._rejected("NOT_ACTIVE_PLAYER", "Only the active player may accept trade.")
        if target is None:
            return self._rejected("INVALID_TRADE", "target_player_id is required.")
        offer = self._pending_trade(player_id, target)
        reason = accept_trade(self.session, player_id, target)
        if reason is not None:
            return self._rejected(
                "TRADE_REJECTED",
                "That trade offer cannot be accepted.",
                {"reason": reason},
            )
        assert offer is not None
        self.session.state_version += 1
        event = self._emit(
            "TradeAccepted",
            self._trade_payload(player_id, target, offer),
            command.command_id,
        )
        return CommandResult(True, self.session.state_version, (event,))

    def _reject_trade(self, command: CommandEnvelope) -> CommandResult:
        player_id = self._active_player(command)
        target = self._target_player(command)
        if player_id is None:
            return self._rejected("NOT_ACTIVE_PLAYER", "Only the active player may reject trade.")
        if target is None:
            return self._rejected("INVALID_TRADE", "target_player_id is required.")
        offer = self._pending_trade(player_id, target)
        reason = reject_trade(self.session, player_id, target)
        if reason is not None:
            return self._rejected(
                "TRADE_REJECTED",
                "That trade offer cannot be rejected.",
                {"reason": reason},
            )
        assert offer is not None
        self.session.state_version += 1
        event = self._emit(
            "TradeRejected",
            self._trade_payload(player_id, target, offer),
            command.command_id,
        )
        return CommandResult(True, self.session.state_version, (event,))

    def _cancel_trade(self, command: CommandEnvelope) -> CommandResult:
        player_id = self._active_player(command)
        target = self._target_player(command)
        if player_id is None:
            return self._rejected("NOT_ACTIVE_PLAYER", "Only the active player may cancel trade.")
        if target is None:
            return self._rejected("INVALID_TRADE", "target_player_id is required.")
        offer = self._pending_trade(player_id, target)
        reason = cancel_trade(self.session, player_id, target)
        if reason is not None:
            return self._rejected(
                "TRADE_REJECTED",
                "That trade offer cannot be cancelled.",
                {"reason": reason},
            )
        assert offer is not None
        self.session.state_version += 1
        event = self._emit(
            "TradeCancelled",
            {
                **self._trade_payload(player_id, target, offer),
                "reason": "withdrawn",
            },
            command.command_id,
        )
        return CommandResult(True, self.session.state_version, (event,))

    def _declare_war(self, command: CommandEnvelope) -> CommandResult:
        """Preserve the base war rule while journaling invalidated trade state."""
        target = self._target_player(command)
        player_id = command.player_id
        offer: TradeOffer | None = None
        if player_id is not None and target is not None:
            offer = self._pending_trade(player_id, target)

        result = super()._declare_war(command)
        if not result.accepted or offer is None or player_id is None or target is None:
            return result
        event = self._emit(
            "TradeCancelled",
            {
                **self._trade_payload(player_id, target, offer),
                "reason": "war_declared",
            },
            command.command_id,
        )
        return CommandResult(
            True,
            self.session.state_version,
            result.events + (event,),
            result.feedback,
        )

    def _append_elimination_events(
        self,
        events: list[EventEnvelope],
        command_id: CommandId,
    ) -> None:
        """Cancel offers involving newly eliminated players with deterministic events."""
        before = len(events)
        super()._append_elimination_events(events, command_id)
        eliminated = [
            PlayerId(str(event.payload["player_id"]))
            for event in events[before:]
            if event.event_type == "PlayerEliminated"
        ]
        for player_id in eliminated:
            self._append_trade_cancellations(events, command_id, player_id, "player_eliminated")

    def _concede(self, command: CommandEnvelope) -> CommandResult:
        """Cancel pending trade offers when a player voluntarily leaves the match."""
        player_id = command.player_id
        result = super()._concede(command)
        if not result.accepted or player_id is None:
            return result
        extra: list[EventEnvelope] = []
        self._append_trade_cancellations(extra, command.command_id, player_id, "player_eliminated")
        if not extra:
            return result
        return CommandResult(
            True,
            self.session.state_version,
            result.events + tuple(extra),
            result.feedback,
        )

    def _append_trade_cancellations(
        self,
        events: list[EventEnvelope],
        command_id: CommandId,
        player_id: PlayerId,
        reason: str,
    ) -> None:
        for counterpart, offer in cancel_trade_offers_for_player(self.session, player_id):
            events.append(
                self._emit(
                    "TradeCancelled",
                    {
                        **self._trade_payload(player_id, counterpart, offer),
                        "reason": reason,
                    },
                    command_id,
                )
            )

    def _pending_trade(self, first: PlayerId, second: PlayerId) -> TradeOffer | None:
        """Read existing bilateral trade state without creating relationship state."""
        if first == second:
            return None
        key = (first, second) if first < second else (second, first)
        relationship = self.session.diplomacy.get(key)
        return relationship.pending_trade if relationship is not None else None

    @staticmethod
    def _trade_amount(command: CommandEnvelope, key: str) -> int | None:
        value = command.payload.get(key, 0)
        if not isinstance(value, int) or isinstance(value, bool) or value < 0:
            return None
        return value

    @staticmethod
    def _trade_payload(
        actor: PlayerId,
        target: PlayerId,
        offer: TradeOffer,
    ) -> dict[str, JsonValue]:
        return {
            "player_id": actor,
            "target_player_id": target,
            "proposer_id": offer.proposer_id,
            "offered_gold": offer.offered_gold,
            "requested_gold": offer.requested_gold,
        }
