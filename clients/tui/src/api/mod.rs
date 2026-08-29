//! API client for communicating with the CivilizationClone backend

use anyhow::Result;
use reqwest::Client;
use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use std::time::Duration;
use crate::logging::log_event;

/// API client for the CivilizationClone HTTP API
pub struct ApiClient {
    client: Client,
    base_url: String,
}

impl ApiClient {
    /// Create a new API client
    pub async fn new(base_url: &str) -> Result<Self> {
        let client = Client::builder()
            .timeout(Duration::from_secs(30))
            .build()?;
        
        Ok(Self {
            client,
            base_url: base_url.to_string(),
        })
    }

    /// Create an API client synchronously (no I/O). Used for lightweight
    /// construction such as `Default` in tests.
    pub fn from_base_url(base_url: &str) -> Self {
        let client = Client::builder()
            .timeout(Duration::from_secs(30))
            .build()
            .expect("failed to build HTTP client");
        Self {
            client,
            base_url: base_url.to_string(),
        }
    }
    
    /// Health check
    pub async fn health(&self) -> Result<HealthResponse> {
        let url = format!("{}/health", self.base_url);
        let response = self.client.get(&url).send().await?;
        Ok(response.json().await?)
    }
    
    /// Get available civilizations
    pub async fn civilizations(&self) -> Result<Vec<Civilization>> {
        let url = format!("{}/api/civilizations", self.base_url);
        let response = self.client.get(&url).send().await?;
        Ok(response.json().await?)
    }
    
    /// Create a new game
    pub async fn create_game(&self, request: CreateGameRequest) -> Result<CreateGameResponse> {
        let url = format!("{}/api/games", self.base_url);
        let response = self.client.post(&url).json(&request).send().await?;
        Ok(response.json().await?)
    }
    
    /// Join a player to a game
    pub async fn join_player(&self, game_id: &str, admin_token: &str, request: JoinPlayerRequest) -> Result<JoinPlayerResponse> {
        let url = format!("{}/api/games/{}/players", self.base_url, game_id);
        let response = self.client
            .post(&url)
            .header("Authorization", format!("Bearer {}", admin_token))
            .json(&request)
            .send()
            .await?;
        Ok(response.json().await?)
    }
    
    /// Start a game
    pub async fn start_game(&self, game_id: &str, admin_token: &str) -> Result<StartGameResponse> {
        let url = format!("{}/api/games/{}/start", self.base_url, game_id);
        let response = self.client
            .post(&url)
            .header("Authorization", format!("Bearer {}", admin_token))
            .send()
            .await?;
        Ok(response.json().await?)
    }
    
    /// Get game state for a player
    pub async fn state(&self, game_id: &str, player_token: &str) -> Result<GameState> {
        let url = format!("{}/api/games/{}/state", self.base_url, game_id);
        let response = self.client
            .get(&url)
            .header("Authorization", format!("Bearer {}", player_token))
            .send()
            .await?;
        Ok(response.json().await?)
    }
    
    /// Get legal actions for a player
    pub async fn legal_actions(&self, game_id: &str, player_token: &str) -> Result<LegalActions> {
        let url = format!("{}/api/games/{}/actions", self.base_url, game_id);
        let response = self.client
            .get(&url)
            .header("Authorization", format!("Bearer {}", player_token))
            .send()
            .await?;
        Ok(response.json().await?)
    }
    
    /// Submit a command
    pub async fn command(&self, game_id: &str, player_token: &str, request: CommandRequest) -> Result<CommandResponse> {
        let url = format!("{}/api/games/{}/command", self.base_url, game_id);
        let raw_resp = self.client
            .post(&url)
            .header("Authorization", format!("Bearer {}", player_token))
            .json(&request)
            .send()
            .await?;
        let resp: CommandResponse = raw_resp.json().await?;
        // Log domain events emitted by this command
        for event in &resp.events {
            // Silently ignore logging errors so they never affect game logic
            let _ = log_event(event);
        }
        Ok(resp)
    }
    
    /// Get events
    pub async fn events(&self, game_id: &str, player_token: &str) -> Result<Vec<GameEvent>> {
        let url = format!("{}/api/games/{}/events", self.base_url, game_id);
        let response = self.client
            .get(&url)
            .header("Authorization", format!("Bearer {}", player_token))
            .send()
            .await?;
        let evts: Vec<GameEvent> = response.json().await?;
        // Log each retrieved domain event
        for event in &evts {
            let _ = log_event(event);
        }
        Ok(evts)
    }
    
    /// Save game
    pub async fn save_game(&self, game_id: &str, player_token: &str, request: SaveGameRequest) -> Result<SaveGameResponse> {
        let url = format!("{}/api/games/{}/save", self.base_url, game_id);
        let response = self.client
            .post(&url)
            .header("Authorization", format!("Bearer {}", player_token))
            .json(&request)
            .send()
            .await?;
        Ok(response.json().await?)
    }
    
    /// Load game
    pub async fn load_game(&self, game_id: &str, admin_token: &str, request: LoadGameRequest) -> Result<LoadGameResponse> {
        let url = format!("{}/api/games/{}/load", self.base_url, game_id);
        let response = self.client
            .post(&url)
            .header("Authorization", format!("Bearer {}", admin_token))
            .json(&request)
            .send()
            .await?;
        Ok(response.json().await?)
    }
    
    /// Get replay data
    pub async fn replay(&self, game_id: &str, player_token: &str) -> Result<ReplayData> {
        let url = format!("{}/api/games/{}/replay", self.base_url, game_id);
        let response = self.client
            .get(&url)
            .header("Authorization", format!("Bearer {}", player_token))
            .send()
            .await?;
        Ok(response.json().await?)
    }
}

// Request/Response types

#[derive(Debug, Serialize, Deserialize)]
pub struct HealthResponse {
    pub status: String,
    pub version: String,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct Civilization {
    pub civilization_id: String,
    pub name: String,
    pub description: String,
    pub tags: Vec<String>,
    pub starting_resources: HashMap<String, i32>,
    pub yield_modifiers: Vec<YieldModifier>,
    pub research_cost_percent: i32,
    pub attack_strength_percent: i32,
    pub defense_strength_percent: i32,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct YieldModifier {
    pub operation: String,
    pub value: i32,
    pub yield_type: String,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct CreateGameRequest {
    pub game_id: String,
    pub seed: u64,
    pub player_count: u8,
    pub map_config: Option<MapConfig>,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct MapConfig {
    pub radius: u8,
    pub land_mass: String,
    pub temperature: String,
    pub moisture: String,
    pub age: String,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct CreateGameResponse {
    pub game_id: String,
    pub admin_token: String,
    pub state_version: u64,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct JoinPlayerRequest {
    pub player_id: String,
    pub name: String,
    pub civilization_id: String,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct JoinPlayerResponse {
    pub accepted: bool,
    pub player_token: Option<String>,
    pub feedback: Vec<Feedback>,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct StartGameResponse {
    pub accepted: bool,
    pub feedback: Vec<Feedback>,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct GameState {
    pub game_id: String,
    pub turn: u32,
    pub status: String,
    pub active_player_id: String,
    pub state_version: u64,
    pub viewer: PlayerView,
    pub map: MapData,
    pub units: Vec<Unit>,
    pub settlements: Vec<Settlement>,
    pub victory: Option<VictoryInfo>,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct PlayerView {
    pub player_id: String,
    pub civilization_id: String,
    pub gold: i32,
    pub science: i32,
    pub culture: i32,
    pub research: ResearchView,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct ResearchView {
    pub selected: Option<String>,
    pub progress: i32,
    pub cost: i32,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct MapData {
    pub radius: u8,
    pub tiles: Vec<MapTile>,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct MapTile {
    pub q: i32,
    pub r: i32,
    pub terrain: String,
    pub visibility: String,
    pub resources: Vec<String>,
    pub improvements: Vec<String>,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct Unit {
    pub unit_id: String,
    pub definition_id: String,
    pub owner_id: String,
    pub q: i32,
    pub r: i32,
    pub hit_points: i32,
    pub movement_remaining: i32,
    pub veteran: bool,
    pub home_city_id: Option<String>,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct Settlement {
    pub settlement_id: String,
    pub owner_id: String,
    pub q: i32,
    pub r: i32,
    pub population: u32,
    pub production: Option<ProductionInfo>,
    pub improvements: Vec<String>,
    pub worked_tiles: Vec<WorkedTile>,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct ProductionInfo {
    pub kind: String,
    pub definition_id: String,
    pub progress: i32,
    pub cost: i32,
    pub turns_remaining: u32,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct WorkedTile {
    pub q: i32,
    pub r: i32,
    pub worked: bool,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct VictoryInfo {
    pub winner_id: String,
    pub victory_type: String,
    pub score: i32,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct LegalActions {
    pub is_active_player: bool,
    pub actions: Vec<String>,
    pub mandatory_decisions: Vec<MandatoryDecision>,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct MandatoryDecision {
    pub decision_type: String,
    pub options: Vec<String>,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct CommandRequest {
    pub command_type: String,
    pub player_id: String,
    pub expected_state_version: u64,
    pub payload: serde_json::Value,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct CommandResponse {
    pub accepted: bool,
    pub events: Vec<GameEvent>,
    pub feedback: Vec<Feedback>,
    pub state_version: u64,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct GameEvent {
    pub sequence: u64,
    pub event_type: String,
    pub payload: serde_json::Value,
    pub turn: u32,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct Feedback {
    pub code: String,
    pub message: String,
    pub severity: String,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct SaveGameRequest {
    pub slot: String,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct SaveGameResponse {
    pub accepted: bool,
    pub feedback: Vec<Feedback>,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct LoadGameRequest {
    pub slot: String,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct LoadGameResponse {
    pub accepted: bool,
    pub feedback: Vec<Feedback>,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct ReplayData {
    pub game_id: String,
    pub events: Vec<GameEvent>,
    pub initial_state: GameState,
}
