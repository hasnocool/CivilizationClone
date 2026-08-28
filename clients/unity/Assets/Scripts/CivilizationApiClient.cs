// clients/unity/Assets/Scripts/CivilizationApiClient.cs
using System;
using System.Collections;
using System.Collections.Generic;
using System.Text;
using UnityEngine;
using UnityEngine.Networking;

namespace CivilizationClone.UnityClient
{
    internal readonly struct ApiResult<T>
    {
        public readonly bool Ok;
        public readonly long Status;
        public readonly string Detail;
        public readonly T Data;

        public ApiResult(bool ok, long status, string detail, T data)
        {
            Ok = ok;
            Status = status;
            Detail = detail;
            Data = data;
        }
    }

    internal sealed class CivilizationApiClient
    {
        private string _baseUrl = "http://127.0.0.1:8000";
        private long _commandNumber;
        private readonly string _clientId = Guid.NewGuid().ToString("N");

        public void Configure(string baseUrl) => _baseUrl = (baseUrl ?? string.Empty).Trim().TrimEnd('/');

        public IEnumerator Health(Action<ApiResult<HealthDto>> done) =>
            Request("GET", "/api/v1/health", null, null, raw => ParseObject(raw, done));

        public IEnumerator Civilizations(Action<ApiResult<CivilizationDto[]>> done) =>
            Request("GET", "/api/v1/rules/civilizations", null, null, raw => ParseArray(raw, done));

        public IEnumerator CreateGame(string gameId, int seed, int players, int radius, Action<ApiResult<GameCreatedDto>> done)
        {
            var body = JsonWire.Object(
                ("game_id", gameId), ("seed", seed), ("player_count", players), ("map_radius", radius),
                ("water_percent", 20), ("resource_percent", 18));
            return Request("POST", "/api/v1/games", body, null, raw => ParseObject(raw, done));
        }

        public IEnumerator JoinPlayer(string gameId, string adminToken, string playerId, string name, string civilizationId, Action<ApiResult<PlayerJoinedDto>> done)
        {
            var body = JsonWire.Object(
                ("command_id", NextCommandId("join")), ("player_id", playerId), ("name", name),
                ("controller", "human"), ("civilization_id", civilizationId));
            return Request("POST", $"/api/v1/games/{Path(gameId)}/players", body, adminToken, raw => ParseObject(raw, done));
        }

        public IEnumerator StartGame(string gameId, string adminToken, Action<ApiResult<CommandResponseDto>> done) =>
            Command(gameId, adminToken, null, -1, "StartGame", new Dictionary<string, object>(), done);

        public IEnumerator Command(string gameId, string token, string playerId, int expectedVersion, string commandType,
            IDictionary<string, object> payload, Action<ApiResult<CommandResponseDto>> done)
        {
            var fields = new List<(string, object)>
            {
                ("command_id", NextCommandId(commandType.ToLowerInvariant())),
                ("command_type", commandType)
            };
            if (!string.IsNullOrEmpty(playerId)) fields.Add(("player_id", playerId));
            if (expectedVersion >= 0) fields.Add(("expected_state_version", expectedVersion));

            var prefix = JsonWire.Object(fields.ToArray());
            var body = prefix.Substring(0, prefix.Length - 1) + ",\"payload\":" + JsonWire.Dictionary(payload) + "}";
            return Request("POST", $"/api/v1/games/{Path(gameId)}/commands", body, token, raw => ParseObject(raw, done));
        }

        public IEnumerator State(string gameId, string token, Action<ApiResult<GameStateDto>> done) =>
            Request("GET", $"/api/v1/games/{Path(gameId)}/state", null, token, raw => ParseObject(raw, done));

        public IEnumerator LegalActions(string gameId, string token, Action<ApiResult<LegalActionsDto>> done) =>
            Request("GET", $"/api/v1/games/{Path(gameId)}/legal-actions", null, token, raw => ParseObject(raw, done));

        public IEnumerator Events(string gameId, string token, int afterSequence, Action<ApiResult<EventDto[]>> done) =>
            Request("GET", $"/api/v1/games/{Path(gameId)}/events?after_sequence={afterSequence}", null, token, raw => ParseArray(raw, done));

        private IEnumerator Request(string method, string path, string body, string token, Action<(bool Ok, long Status, string Detail, string Body)> done)
        {
            using var request = new UnityWebRequest(_baseUrl + path, method);
            request.downloadHandler = new DownloadHandlerBuffer();
            if (body != null)
            {
                request.uploadHandler = new UploadHandlerRaw(Encoding.UTF8.GetBytes(body));
                request.SetRequestHeader("Content-Type", "application/json");
            }
            request.SetRequestHeader("Accept", "application/json");
            if (!string.IsNullOrEmpty(token)) request.SetRequestHeader("Authorization", "Bearer " + token);
            request.timeout = 10;

            yield return request.SendWebRequest();

            var raw = request.downloadHandler?.text ?? string.Empty;
            var ok = request.result == UnityWebRequest.Result.Success && request.responseCode >= 200 && request.responseCode < 300;
            var detail = ok ? string.Empty : ExtractDetail(raw, request.error, request.responseCode);
            done((ok, request.responseCode, detail, raw));
        }

        private static void ParseObject<T>((bool Ok, long Status, string Detail, string Body) raw, Action<ApiResult<T>> done) where T : class
        {
            if (!raw.Ok) { done(new ApiResult<T>(false, raw.Status, raw.Detail, null)); return; }
            try { done(new ApiResult<T>(true, raw.Status, string.Empty, JsonWire.Parse<T>(raw.Body))); }
            catch (Exception error) { done(new ApiResult<T>(false, raw.Status, "Invalid JSON: " + error.Message, null)); }
        }

        private static void ParseArray<T>((bool Ok, long Status, string Detail, string Body) raw, Action<ApiResult<T[]>> done)
        {
            if (!raw.Ok) { done(new ApiResult<T[]>(false, raw.Status, raw.Detail, null)); return; }
            try { done(new ApiResult<T[]>(true, raw.Status, string.Empty, JsonWire.ParseArray<T>(raw.Body))); }
            catch (Exception error) { done(new ApiResult<T[]>(false, raw.Status, "Invalid JSON: " + error.Message, null)); }
        }

        private string NextCommandId(string prefix) => $"unity-{_clientId}-{prefix}-{++_commandNumber}";
        private static string Path(string value) => Uri.EscapeDataString(value ?? string.Empty);

        private static string ExtractDetail(string raw, string fallback, long status)
        {
            if (!string.IsNullOrEmpty(raw))
            {
                var marker = "\"detail\":";
                var index = raw.IndexOf(marker, StringComparison.Ordinal);
                if (index >= 0) return $"HTTP {status}: {raw.Substring(index + marker.Length).Trim().TrimEnd('}')}";
            }
            return $"HTTP {status}: {fallback ?? "request failed"}";
        }
    }
}
