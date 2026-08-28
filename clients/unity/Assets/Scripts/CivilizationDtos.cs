// clients/unity/Assets/Scripts/CivilizationDtos.cs
using System;

namespace CivilizationClone.UnityClient
{
    [Serializable] public sealed class HealthDto { public string status; }

    [Serializable]
    public sealed class CivilizationDto
    {
        public string civilization_id;
        public string name;
        public string description;
        public string[] tags;
        public int research_cost_percent;
        public int attack_strength_percent;
        public int defense_strength_percent;
        public string[] unique_units;
        public string[] unique_buildings;
        public string[] research_preferences;
        public string[] content_hooks;
    }

    [Serializable] public sealed class CivilizationArrayDto { public CivilizationDto[] items; }

    [Serializable]
    public sealed class FeedbackDto
    {
        public string code;
        public string message;
        public string severity;
    }

    [Serializable]
    public sealed class EventDto
    {
        public string event_id;
        public int sequence;
        public string event_type;
        public int state_version;
    }

    [Serializable] public sealed class EventArrayDto { public EventDto[] items; }

    [Serializable]
    public sealed class GameCreatedDto
    {
        public string game_id;
        public int seed;
        public int state_version;
        public string status;
        public string admin_token;
    }

    [Serializable]
    public sealed class PlayerJoinedDto
    {
        public bool accepted;
        public int state_version;
        public string player_id;
        public string civilization_id;
        public string player_token;
        public EventDto[] events;
        public FeedbackDto[] feedback;
    }

    [Serializable]
    public sealed class CommandResponseDto
    {
        public bool accepted;
        public int state_version;
        public EventDto[] events;
        public FeedbackDto[] feedback;
    }

    [Serializable]
    public sealed class ResearchDto
    {
        public string selected;
        public int progress;
        public string[] completed;
        public string[] available;
        public string[] preferences;
    }

    [Serializable]
    public sealed class ViewerDto
    {
        public string player_id;
        public string name;
        public string controller;
        public string civilization_id;
        public int gold;
        public int science;
        public int culture;
        public ResearchDto research;
        public bool eliminated;
    }

    [Serializable]
    public sealed class PlayerDto
    {
        public string player_id;
        public string name;
        public string controller;
        public string civilization_id;
        public bool eliminated;
    }

    [Serializable]
    public sealed class TileDto
    {
        public int q;
        public int r;
        public string visibility;
        public string terrain;
        public string resource;
    }

    [Serializable] public sealed class MapDto { public int radius; public TileDto[] tiles; }

    [Serializable]
    public sealed class UnitDto
    {
        public string unit_id;
        public string owner_id;
        public string definition_id;
        public int q;
        public int r;
        public int movement_remaining;
        public int hit_points;
    }

    [Serializable]
    public sealed class ProductionOrderDto
    {
        public string kind;
        public string definition_id;
        public int cost;
    }

    [Serializable]
    public sealed class SettlementDto
    {
        public string settlement_id;
        public string owner_id;
        public int q;
        public int r;
        public int population;
        public int food_storage;
        public int production_storage;
        public string[] buildings;
        public ProductionOrderDto[] production_queue;
    }

    [Serializable]
    public sealed class DiplomacyDto
    {
        public string other_player_id;
        public string status;
        public string pending_peace_from;
    }

    [Serializable]
    public sealed class VictoryDto
    {
        public string winner_id;
        public string victory_type;
        public int turn;
        public int score;
    }

    [Serializable]
    public sealed class GameStateDto
    {
        public string game_id;
        public int turn;
        public int state_version;
        public string status;
        public string phase;
        public string active_player_id;
        public ViewerDto viewer;
        public PlayerDto[] players;
        public MapDto map;
        public UnitDto[] units;
        public SettlementDto[] settlements;
        public DiplomacyDto[] diplomacy;
        public VictoryDto victory;
    }

    [Serializable]
    public sealed class MandatoryDecisionDto
    {
        public string kind;
        public string[] options;
    }

    [Serializable]
    public sealed class LegalActionsDto
    {
        public string game_id;
        public string player_id;
        public int state_version;
        public bool is_active_player;
        public string[] actions;
        public MandatoryDecisionDto[] mandatory_decisions;
    }
}
