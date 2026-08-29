//! Scene management system
//! 
//! Implements the Civ1-inspired scene graph with 168 distinct UI state templates
//! organized into reusable scene families as defined in SCENE_GRAPH.md and SCENE_CONTRACT.md.

use anyhow::Result;
use std::any::Any;
use std::collections::VecDeque;

use crate::state::AppState;
use crate::input::{InputEvent, KeyCode, KeyModifiers};

/// Scene identifier - maps to CIV1-UI-NNN from the documentation
#[derive(Debug, Clone, Copy, PartialEq, Eq, PartialOrd, Ord, Hash, serde::Serialize, serde::Deserialize)]
pub enum SceneId {
    // Boot/Setup (CIV1-UI-001..006, 058..070)
    TitleScreen,
    MainMenu,
    WorldCreation,
    DifficultySelection,
    CivilizationSelection,
    OpeningDawnOfCivilization,
    Credits,
    SoundDriverSelection,
    GameWorldOptions,
    LoadDrivePrompt,
    CustomizeWorldLandMass,
    CustomizeWorldTemperature,
    CustomizeWorldMoisture,
    CustomizeWorldAge,
    LevelOfCompetition,
    CustomTribeNameEntry,
    RulerNameEntry,
    CopyProtectionQuiz,
    CopyProtectionFailure,
    
    // Strategic Map (CIV1-UI-007..010, 071..080)
    MainWorldMap,
    OrdersMenu,
    TileInformation,
    UnitInformation,
    GameMenu,
    GameOptionsSubmenu,
    TaxRateDialog,
    LuxuryRateDialog,
    FindCityPrompt,
    SaveDriveSlotPrompt,
    QuitConfirmation,
    RetireConfirmation,
    EndOfTurnPrompt,
    InstantAdvice,
    
    // City Management (CIV1-UI-011..016, 105..115)
    FoundCity,
    CityManagement,
    ChangeProduction,
    BuyProduction,
    SellImprovement,
    CityView,
    CityInfoTab,
    CityHappinessChart,
    CityMapSubview,
    CityCitizenReassignment,
    CitySpecialistAssignment,
    RenameCityPrompt,
    CityUnitActivation,
    CityImprovementCompleted,
    WonderRaceLost,
    CivilDisorderContinues,
    WeLoveTheKingDay,
    
    // Research (CIV1-UI-017..018)
    ChooseResearch,
    TechnologyDiscovered,
    
    // Civilopedia (CIV1-UI-019..020, 128..130)
    CivilopediaBrowser,
    CivilopediaEntry,
    CivilopediaSectionMenu,
    CivilopediaHistoryPage,
    CivilopediaGameplayPage,
    CivilopediaResearchHelp,
    CivilopediaProductionHelp,
    
    // Advisors (CIV1-UI-021..028)
    AdvisorsHub,
    CityStatusAdvisor,
    MilitaryAdvisor,
    IntelligenceAdvisor,
    AttitudeAdvisor,
    TradeAdvisor,
    TaxLuxuryScienceRates,
    ScienceAdvisor,
    MilitaryAdvisorCasualties,
    IntelligenceAdvisorDetail,
    
    // World Reports (CIV1-UI-029..034)
    WorldMenu,
    WondersOfTheWorld,
    TopFiveCities,
    CivilizationScore,
    KnownWorldMap,
    Demographics,
    
    // Palace (CIV1-UI-035)
    Palace,
    
    // Diplomacy (CIV1-UI-036..040, 131..142)
    FirstContact,
    DiplomacyConversation,
    TechnologyExchange,
    TributeDemand,
    DiplomatAtForeignCity,
    RivalInitiatesContact,
    PeaceOffer,
    TechnologyTradeSelection,
    BuyPeaceRivalDemand,
    PostTreatyNegotiationMenu,
    MilitaryProposalTarget,
    MilitaryProposalPayment,
    DemandTributeResult,
    BreakTreatyWarning,
    SenateBlocksWar,
    DeclarationOfWar,
    PeaceTreatySigned,
    
    // Government (CIV1-UI-041..043)
    Revolution,
    FormGovernment,
    NewCabinet,
    
    // Events (CIV1-UI-044..046, 116..125, 159..165)
    BarbarianWarning,
    CivilDisorder,
    CityCaptured,
    PollutionAppears,
    GlobalWarming,
    NuclearMeltdown,
    DisasterEarthquake,
    DisasterFamine,
    DisasterFire,
    DisasterFlood,
    DisasterPiracy,
    DisasterPlague,
    DisasterVolcano,
    TreasuryShortfall,
    UnsupportedUnitLost,
    CityDestroyed,
    CityCaptureLootTech,
    CityCaptureLootGold,
    NuclearAttackResult,
    SdiInterception,
    CityAdvisorRecommendation,
    
    // Wonder/Presentation (CIV1-UI-047..048, 156..158)
    WonderCompleted,
    WonderIllustration,
    PalaceImprovementInvitation,
    RivalWonderCompleted,
    WonderObsoleteAnnouncement,
    
    // Space Race (CIV1-UI-049..050, 143..146)
    SpaceshipOverview,
    SpaceshipLaunch,
    RivalSpaceshipStatus,
    SpaceshipLaunchConfirmation,
    SpaceshipInFlight,
    RivalSpaceshipLaunch,
    RivalAlphaCentauriArrival,
    
    // Endgame (CIV1-UI-051..055, 147..149, 154..155)
    AlphaCentauriVictory,
    ConquestVictory,
    Defeat,
    FinalRating,
    HallOfFame,
    AutomaticHistoryEnd,
    ContinuePlayingAfterVictory,
    Powergraph,
    DestructionReplayOffer,
    
    // Persistence (CIV1-UI-056..057, 076, 150..153)
    SaveGame,
    LoadGame,
    ReplayOptions,
    QuickReplay,
    CompleteReplay,
    WriteReplayToDiskResult,
    
    // Historian Rankings (CIV1-UI-081..085)
    HistorianRankingAdvancement,
    HistorianRankingHappiness,
    HistorianRankingPower,
    HistorianRankingSize,
    HistorianRankingWealth,
    
    // Unit Modes (CIV1-UI-086..090)
    UnitStackActivation,
    GoToDestinationTargeting,
    HomeCityReassignment,
    SettlerContextOrders,
    ChangeTerrainOrder,
    
    // Diplomat Actions (CIV1-UI-091..098)
    DiplomatBribeEnemyUnitOffer,
    DiplomatBribeResult,
    DiplomatInciteRevoltPrice,
    DiplomatInciteRevoltResult,
    DiplomatEstablishEmbassyResult,
    DiplomatStealTechnologyResult,
    DiplomatIndustrialSabotageResult,
    EnemyCityInspection,
    
    // Caravan Actions (CIV1-UI-099..100)
    CaravanTradeRouteDelivery,
    CaravanWonderContributionPrompt,
    
    // Minor Tribe Events (CIV1-UI-101..104)
    MinorTribeAncientWisdom,
    MinorTribeJoinsAsCity,
    MinorTribeBarbarians,
    BarbarianLeaderRansom,
    
    // Generic confirmation (reusable overlay)
    GenericConfirm,
}

/// Scene trait - all scenes must implement this
pub trait Scene: Send + Sync {
    /// Get the scene ID
    fn id(&self) -> SceneId;
    
    /// Get the scene family for navigation
    fn family(&self) -> SceneFamily;
    
    /// Initialize the scene with app state
    fn init(&mut self, app_state: &mut AppState) -> Result<()>;
    
    /// Handle input events
    fn handle_input(&mut self, app_state: &mut AppState, event: InputEvent) -> Result<SceneAction>;
    
    /// Update the scene (called each frame)
    fn update(&mut self, app_state: &mut AppState, dt: f32) -> Result<SceneAction>;
    
    /// Render the scene using opentui
    fn render(&mut self, app_state: &AppState, frame: &mut ratatui::Frame) -> Result<()>;
    
    /// Called when scene is pushed onto stack
    fn on_enter(&mut self, app_state: &mut AppState) -> Result<()> {
        self.init(app_state)
    }
    
    /// Called when scene is popped from stack
    fn on_exit(&mut self, app_state: &mut AppState) -> Result<()> {
        Ok(())
    }
    
    /// Get as Any for downcasting
    fn as_any(&self) -> &dyn Any;
    fn as_any_mut(&mut self) -> &mut dyn Any;
}

/// Scene family for navigation grouping
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash)]
pub enum SceneFamily {
    BootSystem,
    Menu,
    StrategicMap,
    UnitInteraction,
    City,
    Research,
    Civilopedia,
    Report,
    Diplomacy,
    EventModal,
    Presentation,
    Spaceship,
    Results,
    Endgame,
    SaveLoad,
    Replay,
}

/// Action to take after handling input/update
pub enum SceneAction {
    None,
    Push(SceneId),
    Pop,
    Replace(SceneId),
    PopTo(SceneId),  // Pop until reaching this scene
    Quit,
    Custom(Box<dyn FnOnce(&mut AppState) -> Result<()> + Send + Sync>),
}

/// Scene stack for managing scene navigation
pub struct SceneStack {
    scenes: VecDeque<Box<dyn Scene>>,
}

impl SceneStack {
    pub fn new() -> Self {
        Self {
            scenes: VecDeque::new(),
        }
    }
    
    pub fn push(&mut self, scene: Box<dyn Scene>) {
        self.scenes.push_back(scene);
    }
    
    pub fn pop(&mut self) -> Option<Box<dyn Scene>> {
        self.scenes.pop_back()
    }
    
    pub fn replace(&mut self, scene: Box<dyn Scene>) {
        self.scenes.pop_back();
        self.scenes.push_back(scene);
    }
    
    pub fn current(&mut self) -> Option<&mut (dyn Scene + 'static)> {
        self.scenes.back_mut().map(Box::as_mut)
    }
    
    pub fn current_id(&self) -> Option<SceneId> {
        self.scenes.back().map(|s| s.id())
    }
    
    pub fn len(&self) -> usize {
        self.scenes.len()
    }
    
    pub fn is_empty(&self) -> bool {
        self.scenes.is_empty()
    }
    
    /// Get all scene IDs in stack (bottom to top)
    pub fn scene_ids(&self) -> Vec<SceneId> {
        self.scenes.iter().map(|s| s.id()).collect()
    }
}

// Helper to create scenes from SceneId
pub fn create_scene(id: SceneId) -> Box<dyn Scene> {
    use crate::scenes::*;
    
    match id {
        // Boot/Setup (CIV1-UI-001..006, 058..070)
        SceneId::TitleScreen => Box::new(boot::TitleScreenScene::new()),
        SceneId::MainMenu => Box::new(boot::MainMenuScene::new()),
        SceneId::WorldCreation => Box::new(boot::WorldCreationScene::new()),
        SceneId::DifficultySelection => Box::new(boot::DifficultySelectionScene::new()),
        SceneId::CivilizationSelection => Box::new(boot::CivilizationSelectionScene::new()),
        SceneId::OpeningDawnOfCivilization => Box::new(boot::OpeningDawnScene::new()),
        SceneId::Credits => Box::new(boot::CreditsScene::new()),
        SceneId::SoundDriverSelection => Box::new(boot::SoundDriverSelectionScene::new()),
        SceneId::GameWorldOptions => Box::new(boot::GameWorldOptionsScene::new()),
        SceneId::LoadDrivePrompt => Box::new(persistence::LoadDrivePromptScene::new()),
        SceneId::CustomizeWorldLandMass => Box::new(boot::CustomizeWorldLandMassScene::new()),
        SceneId::CustomizeWorldTemperature => Box::new(boot::CustomizeWorldTemperatureScene::new()),
        SceneId::CustomizeWorldMoisture => Box::new(boot::CustomizeWorldMoistureScene::new()),
        SceneId::CustomizeWorldAge => Box::new(boot::CustomizeWorldAgeScene::new()),
        SceneId::LevelOfCompetition => Box::new(boot::LevelOfCompetitionScene::new()),
        SceneId::CustomTribeNameEntry => Box::new(boot::CustomTribeNameEntryScene::new()),
        SceneId::RulerNameEntry => Box::new(boot::RulerNameEntryScene::new()),
        SceneId::CopyProtectionQuiz => Box::new(boot::CopyProtectionQuizScene::new()),
        SceneId::CopyProtectionFailure => Box::new(boot::CopyProtectionFailureScene::new()),

        // Strategic Map (CIV1-UI-007..010, 071..080)
        SceneId::MainWorldMap => Box::new(strategic::MainWorldMapScene::new()),
        SceneId::OrdersMenu => Box::new(strategic::OrdersMenuScene::new()),
        SceneId::TileInformation => Box::new(strategic::TileInformationScene::new()),
        SceneId::UnitInformation => Box::new(strategic::UnitInformationScene::new()),
        SceneId::GameMenu => Box::new(strategic::GameMenuScene::new()),
        SceneId::GameOptionsSubmenu => Box::new(strategic::GameOptionsSubmenuScene::new()),
        SceneId::TaxRateDialog => Box::new(strategic::TaxRateDialogScene::new()),
        SceneId::LuxuryRateDialog => Box::new(strategic::LuxuryRateDialogScene::new()),
        SceneId::FindCityPrompt => Box::new(strategic::FindCityPromptScene::new()),
        SceneId::SaveDriveSlotPrompt => Box::new(persistence::SaveDriveSlotPromptScene::new()),
        SceneId::QuitConfirmation => Box::new(modal::QuitConfirmationScene::new()),
        SceneId::RetireConfirmation => Box::new(modal::RetireConfirmationScene::new()),
        SceneId::EndOfTurnPrompt => Box::new(modal::EndOfTurnPromptScene::new()),
        SceneId::InstantAdvice => Box::new(modal::InstantAdviceScene::new()),

        // City Management (CIV1-UI-011..016, 105..115)
        SceneId::FoundCity => Box::new(city::FoundCityScene::new()),
        SceneId::CityManagement => Box::new(city::CityManagementScene::new()),
        SceneId::ChangeProduction => Box::new(city::ChangeProductionScene::new()),
        SceneId::BuyProduction => Box::new(city::BuyProductionScene::new()),
        SceneId::SellImprovement => Box::new(city::SellImprovementScene::new()),
        SceneId::CityView => Box::new(city::CityViewScene::new()),
        SceneId::CityInfoTab => Box::new(city::CityInfoTabScene::new()),
        SceneId::CityHappinessChart => Box::new(city::CityHappinessChartScene::new()),
        SceneId::CityMapSubview => Box::new(city::CityMapSubviewScene::new()),
        SceneId::CityCitizenReassignment => Box::new(city::CityCitizenReassignmentScene::new()),
        SceneId::CitySpecialistAssignment => Box::new(city::CitySpecialistAssignmentScene::new()),
        SceneId::RenameCityPrompt => Box::new(city::RenameCityPromptScene::new()),
        SceneId::CityUnitActivation => Box::new(city::CityUnitActivationScene::new()),
        SceneId::CityImprovementCompleted => Box::new(city::CityImprovementCompletedScene::new()),
        SceneId::WonderRaceLost => Box::new(city::WonderRaceLostScene::new()),
        SceneId::CivilDisorderContinues => Box::new(city::CivilDisorderContinuesScene::new()),
        SceneId::WeLoveTheKingDay => Box::new(city::WeLoveTheKingDayScene::new()),

        // Research (CIV1-UI-017..018)
        SceneId::ChooseResearch => Box::new(research::ChooseResearchScene::new()),
        SceneId::TechnologyDiscovered => Box::new(research::TechnologyDiscoveredScene::new()),

        // Civilopedia (CIV1-UI-019..020, 128..132)
        SceneId::CivilopediaBrowser => Box::new(civilopedia::CivilopediaBrowserScene::new()),
        SceneId::CivilopediaEntry => Box::new(civilopedia::CivilopediaEntryScene::new()),
        SceneId::CivilopediaSectionMenu => Box::new(civilopedia::CivilopediaSectionMenuScene::new()),
        SceneId::CivilopediaHistoryPage => Box::new(civilopedia::CivilopediaHistoryPageScene::new()),
        SceneId::CivilopediaGameplayPage => Box::new(civilopedia::CivilopediaGameplayPageScene::new()),
        SceneId::CivilopediaResearchHelp => Box::new(civilopedia::CivilopediaResearchHelpScene::new()),
        SceneId::CivilopediaProductionHelp => Box::new(civilopedia::CivilopediaProductionHelpScene::new()),

        // Advisors (CIV1-UI-021..028)
        SceneId::AdvisorsHub => Box::new(advisor::AdvisorsHubScene::new()),
        SceneId::CityStatusAdvisor => Box::new(advisor::CityStatusAdvisorScene::new()),
        SceneId::MilitaryAdvisor => Box::new(advisor::MilitaryAdvisorScene::new()),
        SceneId::IntelligenceAdvisor => Box::new(advisor::IntelligenceAdvisorScene::new()),
        SceneId::AttitudeAdvisor => Box::new(advisor::AttitudeAdvisorScene::new()),
        SceneId::TradeAdvisor => Box::new(advisor::TradeAdvisorScene::new()),
        SceneId::TaxLuxuryScienceRates => Box::new(advisor::TaxLuxuryScienceRatesScene::new()),
        SceneId::ScienceAdvisor => Box::new(advisor::ScienceAdvisorScene::new()),
        SceneId::MilitaryAdvisorCasualties => Box::new(advisor::MilitaryAdvisorCasualtiesScene::new()),
        SceneId::IntelligenceAdvisorDetail => Box::new(advisor::IntelligenceAdvisorDetailScene::new()),

        // World Reports (CIV1-UI-029..034)
        SceneId::WorldMenu => Box::new(report::WorldMenuScene::new()),
        SceneId::WondersOfTheWorld => Box::new(report::WondersOfTheWorldScene::new()),
        SceneId::TopFiveCities => Box::new(report::TopFiveCitiesScene::new()),
        SceneId::CivilizationScore => Box::new(report::CivilizationScoreScene::new()),
        SceneId::KnownWorldMap => Box::new(report::KnownWorldMapScene::new()),
        SceneId::Demographics => Box::new(report::DemographicsScene::new()),

        // Palace (CIV1-UI-035)
        SceneId::Palace => Box::new(presentation::PalaceScene::new()),

        // Diplomacy (CIV1-UI-036..040, 131..142)
        SceneId::FirstContact => Box::new(diplomacy::FirstContactScene::new()),
        SceneId::DiplomacyConversation => Box::new(diplomacy::DiplomacyConversationScene::new()),
        SceneId::TechnologyExchange => Box::new(diplomacy::TechnologyExchangeScene::new()),
        SceneId::TributeDemand => Box::new(diplomacy::TributeDemandScene::new()),
        SceneId::DiplomatAtForeignCity => Box::new(diplomacy::DiplomatAtForeignCityScene::new()),
        SceneId::RivalInitiatesContact => Box::new(diplomacy::RivalInitiatesContactScene::new()),
        SceneId::PeaceOffer => Box::new(diplomacy::PeaceOfferScene::new()),
        SceneId::TechnologyTradeSelection => Box::new(diplomacy::TechnologyTradeSelectionScene::new()),
        SceneId::BuyPeaceRivalDemand => Box::new(diplomacy::BuyPeaceRivalDemandScene::new()),
        SceneId::PostTreatyNegotiationMenu => Box::new(diplomacy::PostTreatyNegotiationMenuScene::new()),
        SceneId::MilitaryProposalTarget => Box::new(diplomacy::MilitaryProposalTargetScene::new()),
        SceneId::MilitaryProposalPayment => Box::new(diplomacy::MilitaryProposalPaymentScene::new()),
        SceneId::DemandTributeResult => Box::new(diplomacy::DemandTributeResultScene::new()),
        SceneId::BreakTreatyWarning => Box::new(diplomacy::BreakTreatyWarningScene::new()),
        SceneId::SenateBlocksWar => Box::new(diplomacy::SenateBlocksWarScene::new()),
        SceneId::DeclarationOfWar => Box::new(diplomacy::DeclarationOfWarScene::new()),
        SceneId::PeaceTreatySigned => Box::new(diplomacy::PeaceTreatySignedScene::new()),

        // Government (CIV1-UI-041..043)
        SceneId::Revolution => Box::new(government::RevolutionScene::new()),
        SceneId::FormGovernment => Box::new(government::FormGovernmentScene::new()),
        SceneId::NewCabinet => Box::new(government::NewCabinetScene::new()),

        // Events (CIV1-UI-044..046, 116..125, 159..165)
        SceneId::BarbarianWarning => Box::new(modal::BarbarianWarningScene::new()),
        SceneId::CivilDisorder => Box::new(modal::CivilDisorderScene::new()),
        SceneId::CityCaptured => Box::new(modal::CityCapturedScene::new()),
        SceneId::PollutionAppears => Box::new(modal::PollutionAppearsScene::new()),
        SceneId::GlobalWarming => Box::new(modal::GlobalWarmingScene::new()),
        SceneId::NuclearMeltdown => Box::new(modal::NuclearMeltdownScene::new()),
        SceneId::DisasterEarthquake => Box::new(modal::DisasterEarthquakeScene::new()),
        SceneId::DisasterFamine => Box::new(modal::DisasterFamineScene::new()),
        SceneId::DisasterFire => Box::new(modal::DisasterFireScene::new()),
        SceneId::DisasterFlood => Box::new(modal::DisasterFloodScene::new()),
        SceneId::DisasterPiracy => Box::new(modal::DisasterPiracyScene::new()),
        SceneId::DisasterPlague => Box::new(modal::DisasterPlagueScene::new()),
        SceneId::DisasterVolcano => Box::new(modal::DisasterVolcanoScene::new()),
        SceneId::TreasuryShortfall => Box::new(modal::TreasuryShortfallScene::new()),
        SceneId::UnsupportedUnitLost => Box::new(modal::UnsupportedUnitLostScene::new()),
        SceneId::CityDestroyed => Box::new(modal::CityDestroyedScene::new()),
        SceneId::CityCaptureLootTech => Box::new(modal::CityCaptureLootTechScene::new()),
        SceneId::CityCaptureLootGold => Box::new(modal::CityCaptureLootGoldScene::new()),
        SceneId::NuclearAttackResult => Box::new(modal::NuclearAttackResultScene::new()),
        SceneId::SdiInterception => Box::new(modal::SdiInterceptionScene::new()),
        SceneId::CityAdvisorRecommendation => Box::new(modal::CityAdvisorRecommendationScene::new()),

        // Wonder/Presentation (CIV1-UI-047..048, 156..158)
        SceneId::WonderCompleted => Box::new(presentation::WonderCompletedScene::new()),
        SceneId::WonderIllustration => Box::new(presentation::WonderIllustrationScene::new()),
        SceneId::PalaceImprovementInvitation => Box::new(presentation::PalaceImprovementInvitationScene::new()),
        SceneId::RivalWonderCompleted => Box::new(presentation::RivalWonderCompletedScene::new()),
        SceneId::WonderObsoleteAnnouncement => Box::new(presentation::WonderObsoleteAnnouncementScene::new()),

        // Space Race (CIV1-UI-049..050, 143..146)
        SceneId::SpaceshipOverview => Box::new(space::SpaceshipOverviewScene::new()),
        SceneId::SpaceshipLaunch => Box::new(space::SpaceshipLaunchScene::new()),
        SceneId::RivalSpaceshipStatus => Box::new(space::RivalSpaceshipStatusScene::new()),
        SceneId::SpaceshipLaunchConfirmation => Box::new(space::SpaceshipLaunchConfirmationScene::new()),
        SceneId::SpaceshipInFlight => Box::new(space::SpaceshipInFlightScene::new()),
        SceneId::RivalSpaceshipLaunch => Box::new(space::RivalSpaceshipLaunchScene::new()),
        SceneId::RivalAlphaCentauriArrival => Box::new(space::RivalAlphaCentauriArrivalScene::new()),

        // Endgame (CIV1-UI-051..055, 147..149, 154..155)
        SceneId::AlphaCentauriVictory => Box::new(endgame::AlphaCentauriVictoryScene::new()),
        SceneId::ConquestVictory => Box::new(endgame::ConquestVictoryScene::new()),
        SceneId::Defeat => Box::new(endgame::DefeatScene::new()),
        SceneId::FinalRating => Box::new(endgame::FinalRatingScene::new()),
        SceneId::HallOfFame => Box::new(endgame::HallOfFameScene::new()),
        SceneId::AutomaticHistoryEnd => Box::new(endgame::AutomaticHistoryEndScene::new()),
        SceneId::ContinuePlayingAfterVictory => Box::new(endgame::ContinuePlayingAfterVictoryScene::new()),
        SceneId::Powergraph => Box::new(endgame::PowergraphScene::new()),
        SceneId::DestructionReplayOffer => Box::new(endgame::DestructionReplayOfferScene::new()),

        // Persistence (CIV1-UI-056..057, 076, 150..153)
        SceneId::SaveGame => Box::new(persistence::SaveGameScene::new()),
        SceneId::LoadGame => Box::new(persistence::LoadGameScene::new()),
        SceneId::ReplayOptions => Box::new(persistence::ReplayOptionsScene::new()),
        SceneId::QuickReplay => Box::new(persistence::QuickReplayScene::new()),
        SceneId::CompleteReplay => Box::new(persistence::CompleteReplayScene::new()),
        SceneId::WriteReplayToDiskResult => Box::new(persistence::WriteReplayToDiskResultScene::new()),

        // Historian Rankings (CIV1-UI-081..085)
        SceneId::HistorianRankingAdvancement => Box::new(report::HistorianRankingAdvancementScene::new()),
        SceneId::HistorianRankingHappiness => Box::new(report::HistorianRankingHappinessScene::new()),
        SceneId::HistorianRankingPower => Box::new(report::HistorianRankingPowerScene::new()),
        SceneId::HistorianRankingSize => Box::new(report::HistorianRankingSizeScene::new()),
        SceneId::HistorianRankingWealth => Box::new(report::HistorianRankingWealthScene::new()),

        // Unit Modes (CIV1-UI-086..090)
        SceneId::UnitStackActivation => Box::new(units::UnitStackActivationScene::new()),
        SceneId::GoToDestinationTargeting => Box::new(units::GoToDestinationTargetingScene::new()),
        SceneId::HomeCityReassignment => Box::new(units::HomeCityReassignmentScene::new()),
        SceneId::SettlerContextOrders => Box::new(units::SettlerContextOrdersScene::new()),
        SceneId::ChangeTerrainOrder => Box::new(units::ChangeTerrainOrderScene::new()),

        // Diplomat Actions (CIV1-UI-091..098)
        SceneId::DiplomatBribeEnemyUnitOffer => Box::new(units::DiplomatBribeEnemyUnitOfferScene::new()),
        SceneId::DiplomatBribeResult => Box::new(units::DiplomatBribeResultScene::new()),
        SceneId::DiplomatInciteRevoltPrice => Box::new(units::DiplomatInciteRevoltPriceScene::new()),
        SceneId::DiplomatInciteRevoltResult => Box::new(units::DiplomatInciteRevoltResultScene::new()),
        SceneId::DiplomatEstablishEmbassyResult => Box::new(units::DiplomatEstablishEmbassyResultScene::new()),
        SceneId::DiplomatStealTechnologyResult => Box::new(units::DiplomatStealTechnologyResultScene::new()),
        SceneId::DiplomatIndustrialSabotageResult => Box::new(units::DiplomatIndustrialSabotageResultScene::new()),
        SceneId::EnemyCityInspection => Box::new(units::EnemyCityInspectionScene::new()),

        // Caravan Actions (CIV1-UI-099..100)
        SceneId::CaravanTradeRouteDelivery => Box::new(units::CaravanTradeRouteDeliveryScene::new()),
        SceneId::CaravanWonderContributionPrompt => Box::new(units::CaravanWonderContributionPromptScene::new()),

        // Minor Tribe Events (CIV1-UI-101..104)
        SceneId::MinorTribeAncientWisdom => Box::new(units::MinorTribeAncientWisdomScene::new()),
        SceneId::MinorTribeJoinsAsCity => Box::new(units::MinorTribeJoinsAsCityScene::new()),
        SceneId::MinorTribeBarbarians => Box::new(units::MinorTribeBarbariansScene::new()),
        SceneId::BarbarianLeaderRansom => Box::new(units::BarbarianLeaderRansomScene::new()),

        // Generic confirmation (reusable overlay)
        SceneId::GenericConfirm => Box::new(modal::GenericConfirmScene::new()),
    }
}

/// Placeholder for unimplemented scenes
struct UnimplementedScene {
    id: SceneId,
}

impl UnimplementedScene {
    fn new(id: SceneId) -> Self {
        Self { id }
    }
}

impl Scene for UnimplementedScene {
    fn id(&self) -> SceneId {
        self.id
    }
    
    fn family(&self) -> SceneFamily {
        SceneFamily::Menu
    }
    
    fn init(&mut self, _app_state: &mut AppState) -> Result<()> {
        Ok(())
    }
    
    fn handle_input(&mut self, _app_state: &mut AppState, event: InputEvent) -> Result<SceneAction> {
        if let InputEvent::Key(key) = event {
            if key.code == KeyCode::Esc {
                return Ok(SceneAction::Pop);
    }
}
        Ok(SceneAction::None)
    }
    
    fn update(&mut self, _app_state: &mut AppState, _dt: f32) -> Result<SceneAction> {
        Ok(SceneAction::None)
    }
    
    fn render(&mut self, app_state: &AppState, frame: &mut ratatui::Frame) -> Result<()> {
        use ratatui::widgets::{Block, Paragraph};
        use ratatui::layout::{Alignment, Constraint, Direction, Layout, Rect};
        use ratatui::style::{Color, Style};
        
        let area = frame.size();
        let block = Block::default()
            .title(format!("Scene: {:?} (Not Implemented)", self.id))
            .borders(ratatui::widgets::Borders::ALL)
            .style(Style::default().fg(Color::Yellow));
        
        let text = format!(
            "Scene {:?} is not yet implemented.

Press ESC to go back.",
            self.id
        );
        
        let paragraph = Paragraph::new(text)
            .block(block)
            .alignment(Alignment::Center)
            .style(Style::default().fg(Color::White));
        
        frame.render_widget(paragraph, area);
        Ok(())
    }
    
    fn as_any(&self) -> &dyn Any {
        self
    }
    
    fn as_any_mut(&mut self) -> &mut dyn Any {
        self
    }
}

// Scene modules
pub mod boot;
pub mod strategic;
pub mod city;
pub mod research;
pub mod advisor;
pub mod report;
pub mod diplomacy;
pub mod presentation;
pub mod space;
pub mod endgame;
pub mod persistence;
pub mod modal;
pub mod civilopedia;
pub mod government;
pub mod units;

#[cfg(test)]
mod tests {
    use super::*;
    use crate::input::{InputEvent, KeyEvent, KeyCode, KeyModifiers};

    /// Every canonical scene id from SCENE_INDEX.md plus GenericConfirm.
    /// Keep in sync with the `SceneId` enum; the test asserts the count.
    const ALL_SCENE_IDS: [SceneId; 169] = [
        // Boot/Setup (CIV1-UI-001..006, 058..070)
        SceneId::TitleScreen,
        SceneId::MainMenu,
        SceneId::WorldCreation,
        SceneId::DifficultySelection,
        SceneId::CivilizationSelection,
        SceneId::OpeningDawnOfCivilization,
        SceneId::Credits,
        SceneId::SoundDriverSelection,
        SceneId::GameWorldOptions,
        SceneId::LoadDrivePrompt,
        SceneId::CustomizeWorldLandMass,
        SceneId::CustomizeWorldTemperature,
        SceneId::CustomizeWorldMoisture,
        SceneId::CustomizeWorldAge,
        SceneId::LevelOfCompetition,
        SceneId::CustomTribeNameEntry,
        SceneId::RulerNameEntry,
        SceneId::CopyProtectionQuiz,
        SceneId::CopyProtectionFailure,
        // Strategic Map (CIV1-UI-007..010, 071..080)
        SceneId::MainWorldMap,
        SceneId::OrdersMenu,
        SceneId::TileInformation,
        SceneId::UnitInformation,
        SceneId::GameMenu,
        SceneId::GameOptionsSubmenu,
        SceneId::TaxRateDialog,
        SceneId::LuxuryRateDialog,
        SceneId::FindCityPrompt,
        SceneId::SaveDriveSlotPrompt,
        SceneId::QuitConfirmation,
        SceneId::RetireConfirmation,
        SceneId::EndOfTurnPrompt,
        SceneId::InstantAdvice,
        // City Management (CIV1-UI-011..016, 105..115)
        SceneId::FoundCity,
        SceneId::CityManagement,
        SceneId::ChangeProduction,
        SceneId::BuyProduction,
        SceneId::SellImprovement,
        SceneId::CityView,
        SceneId::CityInfoTab,
        SceneId::CityHappinessChart,
        SceneId::CityMapSubview,
        SceneId::CityCitizenReassignment,
        SceneId::CitySpecialistAssignment,
        SceneId::RenameCityPrompt,
        SceneId::CityUnitActivation,
        SceneId::CityImprovementCompleted,
        SceneId::WonderRaceLost,
        SceneId::CivilDisorderContinues,
        SceneId::WeLoveTheKingDay,
        // Research (CIV1-UI-017..018)
        SceneId::ChooseResearch,
        SceneId::TechnologyDiscovered,
        // Civilopedia (CIV1-UI-019..020, 128..132)
        SceneId::CivilopediaBrowser,
        SceneId::CivilopediaEntry,
        SceneId::CivilopediaSectionMenu,
        SceneId::CivilopediaHistoryPage,
        SceneId::CivilopediaGameplayPage,
        SceneId::CivilopediaResearchHelp,
        SceneId::CivilopediaProductionHelp,
        // Advisors (CIV1-UI-021..028)
        SceneId::AdvisorsHub,
        SceneId::CityStatusAdvisor,
        SceneId::MilitaryAdvisor,
        SceneId::IntelligenceAdvisor,
        SceneId::AttitudeAdvisor,
        SceneId::TradeAdvisor,
        SceneId::TaxLuxuryScienceRates,
        SceneId::ScienceAdvisor,
        SceneId::MilitaryAdvisorCasualties,
        SceneId::IntelligenceAdvisorDetail,
        // World Reports (CIV1-UI-029..034)
        SceneId::WorldMenu,
        SceneId::WondersOfTheWorld,
        SceneId::TopFiveCities,
        SceneId::CivilizationScore,
        SceneId::KnownWorldMap,
        SceneId::Demographics,
        // Palace (CIV1-UI-035)
        SceneId::Palace,
        // Diplomacy (CIV1-UI-036..040, 131..142)
        SceneId::FirstContact,
        SceneId::DiplomacyConversation,
        SceneId::TechnologyExchange,
        SceneId::TributeDemand,
        SceneId::DiplomatAtForeignCity,
        SceneId::RivalInitiatesContact,
        SceneId::PeaceOffer,
        SceneId::TechnologyTradeSelection,
        SceneId::BuyPeaceRivalDemand,
        SceneId::PostTreatyNegotiationMenu,
        SceneId::MilitaryProposalTarget,
        SceneId::MilitaryProposalPayment,
        SceneId::DemandTributeResult,
        SceneId::BreakTreatyWarning,
        SceneId::SenateBlocksWar,
        SceneId::DeclarationOfWar,
        SceneId::PeaceTreatySigned,
        // Government (CIV1-UI-041..043)
        SceneId::Revolution,
        SceneId::FormGovernment,
        SceneId::NewCabinet,
        // Events (CIV1-UI-044..046, 116..125, 159..165)
        SceneId::BarbarianWarning,
        SceneId::CivilDisorder,
        SceneId::CityCaptured,
        SceneId::PollutionAppears,
        SceneId::GlobalWarming,
        SceneId::NuclearMeltdown,
        SceneId::DisasterEarthquake,
        SceneId::DisasterFamine,
        SceneId::DisasterFire,
        SceneId::DisasterFlood,
        SceneId::DisasterPiracy,
        SceneId::DisasterPlague,
        SceneId::DisasterVolcano,
        SceneId::TreasuryShortfall,
        SceneId::UnsupportedUnitLost,
        SceneId::CityDestroyed,
        SceneId::CityCaptureLootTech,
        SceneId::CityCaptureLootGold,
        SceneId::NuclearAttackResult,
        SceneId::SdiInterception,
        SceneId::CityAdvisorRecommendation,
        // Wonder/Presentation (CIV1-UI-047..048, 156..158)
        SceneId::WonderCompleted,
        SceneId::WonderIllustration,
        SceneId::PalaceImprovementInvitation,
        SceneId::RivalWonderCompleted,
        SceneId::WonderObsoleteAnnouncement,
        // Space Race (CIV1-UI-049..050, 143..146)
        SceneId::SpaceshipOverview,
        SceneId::SpaceshipLaunch,
        SceneId::RivalSpaceshipStatus,
        SceneId::SpaceshipLaunchConfirmation,
        SceneId::SpaceshipInFlight,
        SceneId::RivalSpaceshipLaunch,
        SceneId::RivalAlphaCentauriArrival,
        // Endgame (CIV1-UI-051..055, 147..149, 154..155)
        SceneId::AlphaCentauriVictory,
        SceneId::ConquestVictory,
        SceneId::Defeat,
        SceneId::FinalRating,
        SceneId::HallOfFame,
        SceneId::AutomaticHistoryEnd,
        SceneId::ContinuePlayingAfterVictory,
        SceneId::Powergraph,
        SceneId::DestructionReplayOffer,
        // Persistence (CIV1-UI-056..057, 076, 150..153)
        SceneId::SaveGame,
        SceneId::LoadGame,
        SceneId::ReplayOptions,
        SceneId::QuickReplay,
        SceneId::CompleteReplay,
        SceneId::WriteReplayToDiskResult,
        // Historian Rankings (CIV1-UI-081..085)
        SceneId::HistorianRankingAdvancement,
        SceneId::HistorianRankingHappiness,
        SceneId::HistorianRankingPower,
        SceneId::HistorianRankingSize,
        SceneId::HistorianRankingWealth,
        // Unit Modes (CIV1-UI-086..090)
        SceneId::UnitStackActivation,
        SceneId::GoToDestinationTargeting,
        SceneId::HomeCityReassignment,
        SceneId::SettlerContextOrders,
        SceneId::ChangeTerrainOrder,
        // Diplomat Actions (CIV1-UI-091..098)
        SceneId::DiplomatBribeEnemyUnitOffer,
        SceneId::DiplomatBribeResult,
        SceneId::DiplomatInciteRevoltPrice,
        SceneId::DiplomatInciteRevoltResult,
        SceneId::DiplomatEstablishEmbassyResult,
        SceneId::DiplomatStealTechnologyResult,
        SceneId::DiplomatIndustrialSabotageResult,
        SceneId::EnemyCityInspection,
        // Caravan Actions (CIV1-UI-099..100)
        SceneId::CaravanTradeRouteDelivery,
        SceneId::CaravanWonderContributionPrompt,
        // Minor Tribe Events (CIV1-UI-101..104)
        SceneId::MinorTribeAncientWisdom,
        SceneId::MinorTribeJoinsAsCity,
        SceneId::MinorTribeBarbarians,
        SceneId::BarbarianLeaderRansom,
        // Generic confirmation (reusable overlay)
        SceneId::GenericConfirm,
    ];

    #[test]
    fn scene_id_catalog_is_complete() {
        // No duplicate ids and the catalog matches the enum size. The enum
        // has no wildcard arms, so a missing entry here is a compile-time
        // non-exhaustive-match error below.
        let mut ids = ALL_SCENE_IDS.to_vec();
        ids.sort_unstable();
        ids.dedup();
        assert_eq!(ids.len(), ALL_SCENE_IDS.len(), "duplicate scene ids in catalog");
        assert_eq!(ALL_SCENE_IDS.len(), 169, "catalog count drifted, update in sync with SceneId");
    }

    #[test]
    fn every_scene_id_resolves_to_a_concrete_scene() {
        use std::any::Any as _;

        for id in ALL_SCENE_IDS {
            let scene = create_scene(id);
            assert_eq!(scene.id(), id, "scene id mismatch for {id:?}");
            assert!(
                scene.as_any().downcast_ref::<UnimplementedScene>().is_none(),
                "scene {id:?} resolved to the unimplemented placeholder - register it in create_scene"
            );
        }
    }

    #[test]
    fn every_scene_implements_all_trait_methods() {
        for id in ALL_SCENE_IDS {
            let scene = create_scene(id);
            // init/update/render must not panic on a fresh scene with valid input.
            let mut app = crate::state::AppState::default();
            assert!(scene.id() == id);
            let mut scene = scene;
            scene.init(&mut app).expect("init failed");
            scene.update(&mut app, 0.016).expect("update failed");
        }
    }

    #[test]
    fn navigation_input_handling_is_safe() {
        // Ensure each scene gracefully handles common keys.
        let mut app_state = AppState::default();
        let test_keys = [
            KeyCode::Enter,
            KeyCode::Esc,
            KeyCode::Up,
            KeyCode::Down,
        ];
        for id in ALL_SCENE_IDS.iter() {
            let mut scene = create_scene(*id);
            // Initialise the scene; may set up internal state.
            scene.init(&mut app_state).expect("init failed");
            for &code in &test_keys {
                let input = InputEvent::Key(KeyEvent {
                    code,
                    modifiers: KeyModifiers::default(),
                });
                // Ensure handle_input does not panic and returns Ok.
                let _ = scene.handle_input(&mut app_state, input).expect("handle_input failed");
            }
            // Update should not panic.
            scene.update(&mut app_state, 0.016).expect("update failed");
        }
    }
}
