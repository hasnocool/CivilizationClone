// clients/unity/Assets/Scripts/CivilizationClientApp.Network.cs
using System;
using System.Collections;
using System.Collections.Generic;
using System.Linq;

namespace CivilizationClone.UnityClient
{
    public sealed partial class CivilizationClientApp
    {
        private IEnumerator Connect()
        {
            SetStatus("Connecting…");
            _api.Configure(_apiUrl);
            ApiResult<HealthDto> health = default;
            yield return _api.Health(result => health = result);
            if (!Check(health.Ok, health.Detail, "Health check failed")) yield break;

            ApiResult<CivilizationDto[]> civs = default;
            yield return _api.Civilizations(result => civs = result);
            if (!Check(civs.Ok && civs.Data != null && civs.Data.Length > 0, civs.Detail, "Civilization discovery failed")) yield break;
            _civilizations = civs.Data;
            for (var i = 0; i < _civilizationIndices.Length; i++) _civilizationIndices[i] = i % _civilizations.Length;
            _screen = ScreenMode.Lobby;
            SetStatus("Connected. Configure a hotseat game.");
        }

        private IEnumerator CreateAndStartGame()
        {
            if (!int.TryParse(_seedInput, out var seed)) { SetStatus("Seed must be an integer", true); yield break; }
            if (!int.TryParse(_radiusInput, out var radius)) { SetStatus("Radius must be an integer", true); yield break; }
            if (string.IsNullOrWhiteSpace(_gameIdInput)) { SetStatus("Game ID is required", true); yield break; }

            SetStatus("Creating game…");
            ApiResult<GameCreatedDto> created = default;
            yield return _api.CreateGame(_gameIdInput.Trim(), seed, _playerCount, radius, result => created = result);
            if (!Check(created.Ok && created.Data != null, created.Detail, "Create game failed")) yield break;
            _gameId = created.Data.game_id;
            _adminToken = created.Data.admin_token;
            _playerTokens.Clear();

            for (var index = 0; index < _playerCount; index++)
            {
                var civ = CivilizationAt(_civilizationIndices[index]);
                ApiResult<PlayerJoinedDto> joined = default;
                yield return _api.JoinPlayer(_gameId, _adminToken, _playerIds[index].Trim(), _playerNames[index].Trim(), civ.civilization_id, result => joined = result);
                if (!Check(joined.Ok && joined.Data != null && joined.Data.accepted && !string.IsNullOrEmpty(joined.Data.player_token), joined.Detail ?? Feedback(joined.Data?.feedback), $"Player {index + 1} enrollment failed")) yield break;
                _playerTokens[joined.Data.player_id] = joined.Data.player_token;
            }

            ApiResult<CommandResponseDto> started = default;
            yield return _api.StartGame(_gameId, _adminToken, result => started = result);
            if (!Check(started.Ok && started.Data != null && started.Data.accepted, started.Detail ?? Feedback(started.Data?.feedback), "Start game failed")) yield break;

            _adminToken = null; // no longer needed by the client UI
            _viewerId = _playerTokens.Keys.First();
            _viewerGeneration++;
            _lastEventSequence = -1;
            _events.Clear();
            _screen = ScreenMode.Game;
            SetStatus("Game started");
            yield return RefreshGame(_viewerGeneration);
        }

        private IEnumerator RefreshGame(int generation)
        {
            if (_refreshInFlight || _screen != ScreenMode.Game || !_playerTokens.TryGetValue(_viewerId ?? string.Empty, out var token)) yield break;
            _refreshInFlight = true;
            var viewer = _viewerId;

            ApiResult<GameStateDto> state = default;
            yield return _api.State(_gameId, token, result => state = result);
            if (generation != _viewerGeneration || viewer != _viewerId) { _refreshInFlight = false; yield break; }
            if (!state.Ok) { SetStatus("State refresh failed: " + state.Detail, true); _refreshInFlight = false; yield break; }

            ApiResult<LegalActionsDto> legal = default;
            yield return _api.LegalActions(_gameId, token, result => legal = result);
            if (generation != _viewerGeneration || viewer != _viewerId) { _refreshInFlight = false; yield break; }
            if (!legal.Ok) { SetStatus("Legal-action refresh failed: " + legal.Detail, true); _refreshInFlight = false; yield break; }

            ApiResult<EventDto[]> events = default;
            yield return _api.Events(_gameId, token, _lastEventSequence, result => events = result);
            if (generation != _viewerGeneration || viewer != _viewerId) { _refreshInFlight = false; yield break; }
            if (!events.Ok) { SetStatus("Event refresh failed: " + events.Detail, true); _refreshInFlight = false; yield break; }

            _state = state.Data;
            _legal = legal.Data;
            foreach (var item in events.Data ?? Array.Empty<EventDto>())
            {
                _events.Add(item);
                _lastEventSequence = Math.Max(_lastEventSequence, item.sequence);
            }
            if (_events.Count > 100) _events.RemoveRange(0, _events.Count - 100);
            _refreshInFlight = false;
        }

        private void Submit(string commandType, Dictionary<string, object> payload)
        {
            if (_screen != ScreenMode.Game || _state == null || string.IsNullOrEmpty(_viewerId)) return;
            if (!_playerTokens.TryGetValue(_viewerId, out var token)) return;
            StartCoroutine(SubmitRoutine(commandType, payload, token, _viewerGeneration, _viewerId, _state.state_version));
        }

        private IEnumerator SubmitRoutine(string commandType, Dictionary<string, object> payload, string token, int generation, string viewer, int version)
        {
            ApiResult<CommandResponseDto> response = default;
            yield return _api.Command(_gameId, token, viewer, version, commandType, payload, result => response = result);
            if (generation != _viewerGeneration || viewer != _viewerId) yield break;
            if (!response.Ok) { SetStatus($"{commandType} failed: {response.Detail}", true); yield break; }
            if (!response.Data.accepted) { SetStatus(Feedback(response.Data.feedback), true); yield break; }
            SetStatus("Accepted: " + commandType);
            if (commandType == "MoveUnit" || commandType == "AttackUnit" || commandType == "FoundSettlement") _selectedUnitId = null;
            yield return RefreshGame(generation);
        }

    }
}
