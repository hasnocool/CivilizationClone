// clients/unity/Assets/Scripts/CivilizationClientApp.cs
using System;
using System.Collections;
using System.Collections.Generic;
using System.Linq;
using UnityEngine;

namespace CivilizationClone.UnityClient
{
    public sealed partial class CivilizationClientApp : MonoBehaviour
    {
        private enum ScreenMode { Connect, Lobby, Game }

        private readonly CivilizationApiClient _api = new();
        private readonly string[] _playerIds = { "p1", "p2", "p3", "p4" };
        private readonly string[] _playerNames = { "Player 1", "Player 2", "Player 3", "Player 4" };
        private readonly int[] _civilizationIndices = new int[4];
        private readonly Dictionary<string, string> _playerTokens = new();
        private readonly List<EventDto> _events = new();

        private ScreenMode _screen = ScreenMode.Connect;
        private string _apiUrl = "http://127.0.0.1:8000";
        private string _status = "Disconnected";
        private bool _statusError;
        private CivilizationDto[] _civilizations = Array.Empty<CivilizationDto>();
        private string _gameIdInput = "unity-game";
        private string _seedInput = "1";
        private string _radiusInput = "4";
        private int _playerCount = 2;
        private string _gameId;
        private string _adminToken;
        private string _viewerId;
        private int _viewerGeneration;
        private GameStateDto _state;
        private LegalActionsDto _legal;
        private string _selectedUnitId;
        private string _selectedSettlementId;
        private int _selectedQ = int.MaxValue;
        private int _selectedR = int.MaxValue;
        private int _researchIndex;
        private int _diplomacyIndex;
        private string _productionKind = "unit";
        private string _productionId = "settler";
        private int _lastEventSequence = -1;
        private float _nextRefreshAt;
        private bool _refreshInFlight;
        private Vector2 _sideScroll;
        private Vector2 _eventScroll;

        private GUIStyle _titleStyle;
        private GUIStyle _headerStyle;
        private GUIStyle _errorStyle;
        private GUIStyle _statusStyle;
        private GUIStyle _tileStyle;

        private void Awake()
        {
            Application.runInBackground = true;
        }

        private void Update()
        {
            if (_screen == ScreenMode.Game && !_refreshInFlight && Time.unscaledTime >= _nextRefreshAt)
            {
                _nextRefreshAt = Time.unscaledTime + 1f;
                StartCoroutine(RefreshGame(_viewerGeneration));
            }
        }

        private void OnGUI()
        {
            EnsureStyles();
            GUI.Box(new Rect(0, 0, Screen.width, Screen.height), GUIContent.none);
            GUILayout.BeginArea(new Rect(16, 12, Screen.width - 32, Screen.height - 24));
            GUILayout.Label("CivilizationClone — Unity Client", _titleStyle);
            GUILayout.Label(_status, _statusError ? _errorStyle : _statusStyle);
            GUILayout.Space(6);

            switch (_screen)
            {
                case ScreenMode.Connect: DrawConnection(); break;
                case ScreenMode.Lobby: DrawLobby(); break;
                case ScreenMode.Game: DrawGame(); break;
            }
            GUILayout.EndArea();
        }

        private void DrawConnection()
        {
            GUILayout.BeginHorizontal();
            GUILayout.Label("API", GUILayout.Width(36));
            _apiUrl = GUILayout.TextField(_apiUrl, GUILayout.ExpandWidth(true));
            if (GUILayout.Button("Connect", GUILayout.Width(120))) StartCoroutine(Connect());
            GUILayout.EndHorizontal();
        }

        private void DrawLobby()
        {
            GUILayout.Label("New hotseat game", _headerStyle);
            GUILayout.BeginHorizontal();
            LabelField("Game ID", ref _gameIdInput, 110);
            LabelField("Seed", ref _seedInput, 70);
            LabelField("Radius", ref _radiusInput, 60);
            GUILayout.Label("Players", GUILayout.Width(55));
            if (GUILayout.Button("−", GUILayout.Width(28))) _playerCount = Mathf.Max(2, _playerCount - 1);
            GUILayout.Label(_playerCount.ToString(), GUILayout.Width(22));
            if (GUILayout.Button("+", GUILayout.Width(28))) _playerCount = Mathf.Min(4, _playerCount + 1);
            GUILayout.EndHorizontal();

            GUILayout.Space(8);
            for (var index = 0; index < _playerCount; index++)
            {
                GUILayout.BeginHorizontal();
                _playerIds[index] = GUILayout.TextField(_playerIds[index], GUILayout.Width(90));
                _playerNames[index] = GUILayout.TextField(_playerNames[index], GUILayout.Width(180));
                var civ = CivilizationAt(_civilizationIndices[index]);
                if (GUILayout.Button(civ?.name ?? "No civilization", GUILayout.Width(220)))
                    _civilizationIndices[index] = _civilizations.Length == 0 ? 0 : (_civilizationIndices[index] + 1) % _civilizations.Length;
                if (civ != null) GUILayout.Label(civ.description, GUILayout.ExpandWidth(true));
                GUILayout.EndHorizontal();
            }

            GUILayout.Space(10);
            if (GUILayout.Button("Create & Start Game", GUILayout.Height(34))) StartCoroutine(CreateAndStartGame());
        }

        private void DrawGame()
        {
            DrawGameToolbar();
            var bodyHeight = Screen.height - 130;
            GUILayout.BeginHorizontal(GUILayout.Height(bodyHeight));
            DrawMap(Mathf.Max(500f, Screen.width - 470f), bodyHeight);
            DrawSidePanel(420f, bodyHeight);
            GUILayout.EndHorizontal();
        }

        private void DrawGameToolbar()
        {
            GUILayout.BeginHorizontal();
            GUILayout.Label("Viewer", GUILayout.Width(50));
            if (GUILayout.Button(_viewerId ?? "-", GUILayout.Width(100))) CycleViewer();
            if (GUILayout.Button("Refresh", GUILayout.Width(90))) StartCoroutine(RefreshGame(_viewerGeneration));
            GUILayout.FlexibleSpace();
            if (_state?.viewer != null)
            {
                var research = _state.viewer.research?.selected ?? "-";
                GUILayout.Label($"Turn {_state.turn} | active {_state.active_player_id ?? "-"} | {_state.viewer.civilization_id} | G {_state.viewer.gold} S {_state.viewer.science} C {_state.viewer.culture} | research {research}");
            }
            GUILayout.EndHorizontal();
        }

        private void DrawMap(float width, float height)
        {
            GUILayout.BeginVertical(GUILayout.Width(width), GUILayout.Height(height));
            var mapRect = GUILayoutUtility.GetRect(width, height - 10, GUILayout.ExpandWidth(false), GUILayout.ExpandHeight(false));
            GUI.Box(mapRect, GUIContent.none);
            if (_state?.map?.tiles == null) { GUI.Label(mapRect, "No map state"); GUILayout.EndVertical(); return; }

            const float tileWidth = 72f;
            const float tileHeight = 44f;
            var radius = Mathf.Max(2, _state.map.radius);
            var scaleX = Mathf.Min(tileWidth, (mapRect.width - 40f) / (radius * 3f + 2f));
            var scaleY = Mathf.Min(tileHeight, (mapRect.height - 40f) / (radius * 2.2f + 2f));
            var centerX = mapRect.x + mapRect.width * 0.5f;
            var centerY = mapRect.y + mapRect.height * 0.5f;

            foreach (var tile in _state.map.tiles)
            {
                var x = centerX + tile.q * scaleX * 0.78f;
                var y = centerY + (tile.r + tile.q * 0.5f) * scaleY;
                var rect = new Rect(x - scaleX * 0.46f, y - scaleY * 0.42f, scaleX * 0.92f, scaleY * 0.84f);
                var label = TileLabel(tile);
                var oldColor = GUI.backgroundColor;
                GUI.backgroundColor = TileColor(tile);
                if (GUI.Button(rect, label, _tileStyle)) HandleTileClick(tile.q, tile.r);
                GUI.backgroundColor = oldColor;
            }
            GUILayout.EndVertical();
        }

        private void DrawSidePanel(float width, float height)
        {
            GUILayout.BeginVertical(GUILayout.Width(width), GUILayout.Height(height));
            _sideScroll = GUILayout.BeginScrollView(_sideScroll, GUILayout.Width(width), GUILayout.Height(height));
            GUILayout.Label("Selection", _headerStyle);
            GUILayout.Label(SelectionText());
            if (GUILayout.Button("Found Settlement (selected unit)"))
                Submit("FoundSettlement", D(("unit_id", _selectedUnitId)));

            GUILayout.Space(8);
            GUILayout.Label("Research", _headerStyle);
            var research = CurrentResearchOptions();
            if (research.Length > 0)
            {
                _researchIndex = Mathf.Clamp(_researchIndex, 0, research.Length - 1);
                if (GUILayout.Button("Research: " + research[_researchIndex])) _researchIndex = (_researchIndex + 1) % research.Length;
                if (GUILayout.Button("Choose Research")) Submit("ChooseResearch", D(("technology_id", research[_researchIndex])));
            }
            else GUILayout.Label("No selectable research");

            GUILayout.Space(8);
            GUILayout.Label("Settlement / Production", _headerStyle);
            GUILayout.Label("Settlement: " + (_selectedSettlementId ?? "none"));
            GUILayout.BeginHorizontal();
            if (GUILayout.Button("Work selected tile")) SetWorkedTile(true);
            if (GUILayout.Button("Unwork selected tile")) SetWorkedTile(false);
            GUILayout.EndHorizontal();
            if (GUILayout.Button("Kind: " + _productionKind)) _productionKind = _productionKind == "unit" ? "building" : "unit";
            _productionId = GUILayout.TextField(_productionId);
            if (GUILayout.Button("Queue Production"))
                Submit("QueueProduction", D(("settlement_id", _selectedSettlementId), ("kind", _productionKind), ("definition_id", _productionId)));
            if (GUILayout.Button("Cancel First Queue Item"))
                Submit("CancelProduction", D(("settlement_id", _selectedSettlementId), ("index", 0)));

            GUILayout.Space(8);
            GUILayout.Label("Diplomacy", _headerStyle);
            var diplomacy = _state?.diplomacy ?? Array.Empty<DiplomacyDto>();
            if (diplomacy.Length > 0)
            {
                _diplomacyIndex = Mathf.Clamp(_diplomacyIndex, 0, diplomacy.Length - 1);
                var relation = diplomacy[_diplomacyIndex];
                if (GUILayout.Button($"Target: {relation.other_player_id} ({relation.status})")) _diplomacyIndex = (_diplomacyIndex + 1) % diplomacy.Length;
                GUILayout.BeginHorizontal();
                if (GUILayout.Button("Declare War")) Diplomacy("DeclareWar");
                if (GUILayout.Button("Offer Peace")) Diplomacy("OfferPeace");
                GUILayout.EndHorizontal();
                GUILayout.BeginHorizontal();
                if (GUILayout.Button("Accept Peace")) Diplomacy("AcceptPeace");
                if (GUILayout.Button("Reject Peace")) Diplomacy("RejectPeace");
                GUILayout.EndHorizontal();
            }

            GUILayout.Space(8);
            GUILayout.Label("Turn", _headerStyle);
            GUILayout.BeginHorizontal();
            if (GUILayout.Button("End Turn")) Submit("EndTurn", D());
            if (GUILayout.Button("Concede")) Submit("Concede", D());
            GUILayout.EndHorizontal();

            GUILayout.Space(8);
            GUILayout.Label("Legal actions", _headerStyle);
            GUILayout.Label(_legal == null ? "-" : string.Join(", ", _legal.actions ?? Array.Empty<string>()));
            if (_legal?.mandatory_decisions != null)
                foreach (var decision in _legal.mandatory_decisions) GUILayout.Label($"Mandatory {decision.kind}: {string.Join(", ", decision.options ?? Array.Empty<string>())}");

            GUILayout.Space(8);
            GUILayout.Label("Authorized events", _headerStyle);
            _eventScroll = GUILayout.BeginScrollView(_eventScroll, GUILayout.Height(210));
            foreach (var item in _events.Skip(Math.Max(0, _events.Count - 40))) GUILayout.Label($"#{item.sequence} {item.event_type}");
            GUILayout.EndScrollView();
            GUILayout.EndScrollView();
            GUILayout.EndVertical();
        }

    }
}
