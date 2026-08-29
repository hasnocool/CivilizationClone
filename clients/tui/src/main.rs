//! CivilizationClone TUI Client
//! 
//! A terminal user interface for CivilizationClone using ratatui and bevy,
//! implementing the Civ1-inspired UI/UX as defined in docs/ui/civ1/.

use anyhow::Result;

mod logging;

mod api;
mod components;
mod input;
mod scenes;
mod state;
mod systems;

use crate::state::AppState;
use crate::systems::run_app;

#[tokio::main]
async fn main() -> Result<()> {
    // Initialize logging (writes to separate files)
    logging::init_logging()?;

    // Initialize application state
    let mut app_state = AppState::new().await?;

    // Run the application
    run_app(&mut app_state).await?;

    Ok(())
}
