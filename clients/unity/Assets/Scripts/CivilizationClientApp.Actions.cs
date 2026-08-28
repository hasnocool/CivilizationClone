// clients/unity/Assets/Scripts/CivilizationClientApp.Actions.cs
using System;
using System.Collections.Generic;
using System.Linq;
using UnityEngine;

namespace CivilizationClone.UnityClient
{
    public sealed partial class CivilizationClientApp
    {
        private void HandleTileClick(int q, int r)
        {
            _selectedQ = q; _selectedR = r;
            var ownUnit = (_state?.units ?? Array.Empty<UnitDto>()).FirstOrDefault(unit => unit.q == q && unit.r == r && unit.owner_id == _viewerId);
            if (ownUnit != null) { _selectedUnitId = ownUnit.unit_id; return; }
            var enemy = (_state?.units ?? Array.Empty<UnitDto>()).FirstOrDefault(unit => unit.q == q && unit.r == r && unit.owner_id != _viewerId);
            if (enemy != null && !string.IsNullOrEmpty(_selectedUnitId)) { Submit("AttackUnit", D(("attacker_id", _selectedUnitId), ("defender_id", enemy.unit_id))); return; }
            var settlement = (_state?.settlements ?? Array.Empty<SettlementDto>()).FirstOrDefault(city => city.q == q && city.r == r && city.owner_id == _viewerId);
            if (settlement != null) { _selectedSettlementId = settlement.settlement_id; return; }
            if (!string.IsNullOrEmpty(_selectedUnitId)) Submit("MoveUnit", D(("unit_id", _selectedUnitId), ("q", q), ("r", r)));
        }

        private void SetWorkedTile(bool worked)
        {
            if (string.IsNullOrEmpty(_selectedSettlementId) || _selectedQ == int.MaxValue) { SetStatus("Choose a settlement and map tile first", true); return; }
            Submit("SetWorkedTile", D(("settlement_id", _selectedSettlementId), ("q", _selectedQ), ("r", _selectedR), ("worked", worked)));
        }

        private void Diplomacy(string commandType)
        {
            var relations = _state?.diplomacy ?? Array.Empty<DiplomacyDto>();
            if (relations.Length == 0) return;
            _diplomacyIndex = Mathf.Clamp(_diplomacyIndex, 0, relations.Length - 1);
            Submit(commandType, D(("target_player_id", relations[_diplomacyIndex].other_player_id)));
        }

        private void CycleViewer()
        {
            if (_playerTokens.Count == 0) return;
            var ids = _playerTokens.Keys.ToArray();
            var index = Array.IndexOf(ids, _viewerId);
            _viewerId = ids[(index + 1 + ids.Length) % ids.Length];
            _viewerGeneration++;
            _state = null;
            _legal = null;
            _selectedUnitId = null;
            _selectedSettlementId = null;
            _selectedQ = _selectedR = int.MaxValue;
            _lastEventSequence = -1;
            _events.Clear();
            _refreshInFlight = false;
            _nextRefreshAt = 0f;
            SetStatus("Viewer switched to " + _viewerId);
        }

        private string[] CurrentResearchOptions()
        {
            var options = _state?.viewer?.research?.available;
            if (options is { Length: > 0 }) return options;
            var mandatory = _legal?.mandatory_decisions?.FirstOrDefault(item => item.kind == "research");
            return mandatory?.options ?? Array.Empty<string>();
        }

        private string TileLabel(TileDto tile)
        {
            var terrain = string.IsNullOrEmpty(tile.terrain) ? "?" : tile.terrain.Substring(0, Mathf.Min(2, tile.terrain.Length)).ToUpperInvariant();
            var marker = "";
            var unit = (_state?.units ?? Array.Empty<UnitDto>()).FirstOrDefault(item => item.q == tile.q && item.r == tile.r);
            if (unit != null) marker = unit.owner_id == _viewerId ? " U" : " E";
            var city = (_state?.settlements ?? Array.Empty<SettlementDto>()).FirstOrDefault(item => item.q == tile.q && item.r == tile.r);
            if (city != null) marker += city.owner_id == _viewerId ? " C" : " X";
            return $"{terrain}{marker}\n{tile.q},{tile.r}";
        }

        private static Color TileColor(TileDto tile)
        {
            if (tile.visibility == "discovered") return new Color(0.35f, 0.35f, 0.38f);
            return tile.terrain switch
            {
                "water" => new Color(0.25f, 0.45f, 0.72f),
                "grassland" => new Color(0.38f, 0.63f, 0.32f),
                "plains" => new Color(0.62f, 0.68f, 0.36f),
                "hills" => new Color(0.56f, 0.48f, 0.35f),
                "desert" => new Color(0.78f, 0.67f, 0.38f),
                "tundra" => new Color(0.65f, 0.68f, 0.70f),
                _ => Color.gray
            };
        }

        private string SelectionText()
        {
            var parts = new List<string>();
            if (!string.IsNullOrEmpty(_selectedUnitId)) parts.Add("unit " + _selectedUnitId);
            if (!string.IsNullOrEmpty(_selectedSettlementId)) parts.Add("settlement " + _selectedSettlementId);
            if (_selectedQ != int.MaxValue) parts.Add($"tile ({_selectedQ},{_selectedR})");
            return parts.Count == 0 ? "none" : string.Join(", ", parts);
        }

        private CivilizationDto CivilizationAt(int index) => _civilizations.Length == 0 ? null : _civilizations[Mathf.Clamp(index, 0, _civilizations.Length - 1)];
        private static Dictionary<string, object> D(params (string Key, object Value)[] values) => values.ToDictionary(value => value.Key, value => value.Value);

        private static string Feedback(FeedbackDto[] feedback) => feedback == null || feedback.Length == 0
            ? "Command rejected"
            : string.Join(" | ", feedback.Select(item => $"{item.code}: {item.message}"));

        private bool Check(bool ok, string detail, string prefix)
        {
            if (ok) return true;
            SetStatus(prefix + (string.IsNullOrEmpty(detail) ? string.Empty : ": " + detail), true);
            return false;
        }

        private void SetStatus(string text, bool error = false) { _status = text; _statusError = error; }

        private static void LabelField(string label, ref string value, float width)
        {
            GUILayout.Label(label, GUILayout.Width(55));
            value = GUILayout.TextField(value, GUILayout.Width(width));
        }

        private void EnsureStyles()
        {
            _titleStyle ??= new GUIStyle(GUI.skin.label) { fontSize = 24, fontStyle = FontStyle.Bold };
            _headerStyle ??= new GUIStyle(GUI.skin.label) { fontSize = 17, fontStyle = FontStyle.Bold };
            _errorStyle ??= new GUIStyle(GUI.skin.label) { normal = { textColor = new Color(1f, 0.45f, 0.4f) } };
            _statusStyle ??= new GUIStyle(GUI.skin.label) { normal = { textColor = new Color(0.72f, 0.78f, 0.85f) } };
            _tileStyle ??= new GUIStyle(GUI.skin.button) { fontSize = 11, alignment = TextAnchor.MiddleCenter, wordWrap = false };
        }
    }
}
