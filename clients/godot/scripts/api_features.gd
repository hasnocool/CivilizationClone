class_name CivilizationApiFeatures
extends Node

const EventStream := preload("res://scripts/event_stream.gd")

var _main: Node
var _api: CivilizationApiClient
var _stream: CivilizationEventStream
var _water_spin: SpinBox
var _resource_spin: SpinBox
var _attach_game_edit: LineEdit
var _attach_player_edit: LineEdit
var _attach_token_edit: LineEdit
var _stream_status: Label
var _controller_scan_pending := false
var _stream_bootstrap_running := false
var _session_key := ""
var _event_cursor := -1
var _event_history: Array = []
var _refresh_pending := false

func _ready() -> void:
	call_deferred("_install")

func _exit_tree() -> void:
	if get_tree() != null and get_tree().node_added.is_connected(_on_node_added):
		get_tree().node_added.disconnect(_on_node_added)

func _process(_delta: float) -> void:
	if _main == null or _api == null:
		return
	var game_id := str(_main.get("game_id"))
	var viewer_id := str(_main.get("viewer_id"))
	var tokens: Dictionary = _main.get("player_tokens")
	var token := str(tokens.get(viewer_id, ""))
	var desired_key := "%s|%s" % [game_id, viewer_id]
	if game_id.is_empty() or viewer_id.is_empty() or token.is_empty():
		if not _session_key.is_empty():
			_reset_stream_session()
		return
	if desired_key != _session_key and not _stream_bootstrap_running:
		_bootstrap_stream_session(game_id, viewer_id, token)

func _install() -> void:
	_main = get_parent()
	if _main == null:
		return
	_api = _main.get("api") as CivilizationApiClient
	if _api == null:
		return

	_stream = EventStream.new()
	_stream.name = "AuthorizedEventStream"
	add_child(_stream)
	_stream.event_received.connect(_on_stream_event)
	_stream.status_changed.connect(_on_stream_status)
	_stream.stream_error.connect(_on_stream_error)

	_install_advanced_game_options()
	_install_attach_panel()
	_install_game_session_controls()
	_scan_player_rows()
	get_tree().node_added.connect(_on_node_added)
	set_process(true)

func _install_advanced_game_options() -> void:
	var lobby := _main.get("lobby_panel") as Control
	if lobby == null:
		return
	var parameters := _find_first_grid(lobby)
	if parameters == null:
		return

	parameters.add_child(_field_label("Water %"))
	_water_spin = SpinBox.new()
	_water_spin.name = "WaterPercentSpin"
	_water_spin.min_value = 0
	_water_spin.max_value = 60
	_water_spin.step = 1
	_water_spin.value = 20
	_water_spin.tooltip_text = "Map-generation water percentage sent to POST /api/v1/games."
	_water_spin.value_changed.connect(_on_map_option_changed)
	parameters.add_child(_water_spin)

	parameters.add_child(_field_label("Resources %"))
	_resource_spin = SpinBox.new()
	_resource_spin.name = "ResourcePercentSpin"
	_resource_spin.min_value = 0
	_resource_spin.max_value = 60
	_resource_spin.step = 1
	_resource_spin.value = 18
	_resource_spin.tooltip_text = "Map-generation resource percentage sent to POST /api/v1/games."
	_resource_spin.value_changed.connect(_on_map_option_changed)
	parameters.add_child(_resource_spin)
	_on_map_option_changed(0.0)

func _install_attach_panel() -> void:
	var panel := _main.get("connection_panel") as PanelContainer
	if panel == null or panel.get_child_count() == 0:
		return
	var existing := panel.get_child(0)
	var shell := VBoxContainer.new()
	shell.name = "ConnectionAndAttach"
	shell.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	shell.add_theme_constant_override("separation", 10)
	panel.add_child(shell)
	existing.reparent(shell)

	var heading := Label.new()
	heading.text = "Attach to existing game"
	heading.add_theme_font_size_override("font_size", 17)
	shell.add_child(heading)

	var help := Label.new()
	help.text = "Use an existing player credential. The token stays in memory only and is never placed in a URL."
	help.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	help.modulate = Color("94a3b8")
	shell.add_child(help)

	var grid := GridContainer.new()
	grid.name = "AttachExistingGrid"
	grid.columns = 2
	grid.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	shell.add_child(grid)

	grid.add_child(_field_label("Game ID"))
	_attach_game_edit = LineEdit.new()
	_attach_game_edit.name = "AttachGameIdEdit"
	_attach_game_edit.placeholder_text = "existing game id"
	grid.add_child(_attach_game_edit)

	grid.add_child(_field_label("Player ID"))
	_attach_player_edit = LineEdit.new()
	_attach_player_edit.name = "AttachPlayerIdEdit"
	_attach_player_edit.placeholder_text = "optional; verified against token"
	grid.add_child(_attach_player_edit)

	grid.add_child(_field_label("Player token"))
	_attach_token_edit = LineEdit.new()
	_attach_token_edit.name = "AttachPlayerTokenEdit"
	_attach_token_edit.placeholder_text = "Bearer credential"
	_attach_token_edit.secret = true
	_attach_token_edit.secret_character = "•"
	grid.add_child(_attach_token_edit)

	var attach_button := Button.new()
	attach_button.name = "AttachExistingButton"
	attach_button.text = "Attach Existing Game"
	attach_button.pressed.connect(_attach_existing_game)
	shell.add_child(attach_button)

func _install_game_session_controls() -> void:
	var viewer_select := _main.get("viewer_select") as OptionButton
	if viewer_select == null or viewer_select.get_parent() == null:
		return
	var top := viewer_select.get_parent() as Container
	if top == null:
		return

	_stream_status = Label.new()
	_stream_status.name = "LiveEventStatus"
	_stream_status.text = "Live events: offline"
	_stream_status.tooltip_text = "Authorized WebSocket event stream status."
	_stream_status.modulate = Color("94a3b8")
	top.add_child(_stream_status)

	var clear_button := Button.new()
	clear_button.name = "ClearSessionButton"
	clear_button.text = "Disconnect / Clear Session"
	clear_button.tooltip_text = "Close the event stream, clear in-memory credentials, and return to connection setup."
	clear_button.pressed.connect(_clear_session)
	top.add_child(clear_button)

func _on_node_added(node: Node) -> void:
	if _main == null or node == _main or not _main.is_ancestor_of(node):
		return
	var player_box := _main.get("player_config_box") as VBoxContainer
	if player_box == null:
		return
	if node == player_box or player_box.is_ancestor_of(node):
		_schedule_player_row_scan()

func _schedule_player_row_scan() -> void:
	if _controller_scan_pending:
		return
	_controller_scan_pending = true
	call_deferred("_scan_player_rows")

func _scan_player_rows() -> void:
	_controller_scan_pending = false
	if _main == null or _api == null:
		return
	var player_box := _main.get("player_config_box") as VBoxContainer
	if player_box == null:
		return
	for row in player_box.get_children():
		if not row is Container or bool(row.get_meta("api_controller_installed", false)):
			continue
		var player_id_edit := _first_line_edit(row)
		if player_id_edit == null:
			continue
		var selector := OptionButton.new()
		selector.name = "ControllerSelect"
		selector.add_item("Human")
		selector.set_item_metadata(0, "human")
		selector.add_item("Bot")
		selector.set_item_metadata(1, "bot")
		selector.tooltip_text = "Controller type sent through the public player-enrollment API."
		row.add_child(selector)
		row.set_meta("api_controller_installed", true)
		selector.item_selected.connect(func(index: int) -> void:
			var player_id := player_id_edit.text.strip_edges()
			if not player_id.is_empty():
				_api.set_player_controller(player_id, str(selector.get_item_metadata(index)))
		)
		player_id_edit.text_changed.connect(func(_text: String) -> void:
			var player_id := player_id_edit.text.strip_edges()
			if not player_id.is_empty():
				_api.set_player_controller(player_id, str(selector.get_item_metadata(selector.selected)))
		)
		_api.set_player_controller(player_id_edit.text.strip_edges(), "human")

func _on_map_option_changed(_value: float) -> void:
	if _api == null or _water_spin == null or _resource_spin == null:
		return
	_api.configure_game_options(int(_water_spin.value), int(_resource_spin.value))

func _attach_existing_game() -> void:
	if _api == null:
		return
	var game_id := _attach_game_edit.text.strip_edges()
	var supplied_player_id := _attach_player_edit.text.strip_edges()
	var token := _attach_token_edit.text.strip_edges()
	if game_id.is_empty() or token.is_empty():
		_set_main_status("Game ID and player token are required", true)
		return

	var api_url_edit := _main.get("api_url_edit") as LineEdit
	if api_url_edit != null:
		_api.configure(api_url_edit.text)
	_set_main_status("Attaching to existing game…")

	var health := await _api.health()
	if not bool(health.get("ok", false)):
		_set_main_status("Health check failed: %s" % health.get("detail", "unknown error"), true)
		return
	var state_response := await _api.state(game_id, token)
	if not bool(state_response.get("ok", false)):
		_set_main_status("Attach failed: %s" % state_response.get("detail", "unknown error"), true)
		return
	if not state_response.get("data") is Dictionary:
		_set_main_status("Attach failed: state response was not an object", true)
		return
	var projection: Dictionary = state_response["data"]
	var resolved_player_id := str(projection.get("viewer", {}).get("player_id", ""))
	if resolved_player_id.is_empty():
		_set_main_status("Attach failed: server projection did not identify the viewer", true)
		return
	if not supplied_player_id.is_empty() and supplied_player_id != resolved_player_id:
		_set_main_status("Attach failed: player ID does not match the credential", true)
		return

	_main.set("game_id", game_id)
	_main.set("admin_token", "")
	_main.set("viewer_id", resolved_player_id)
	_main.set("selected_unit_id", "")
	_main.set("selected_settlement_id", "")
	_main.set("selected_tile", Vector2i(999999, 999999))
	var tokens: Dictionary = {}
	tokens[resolved_player_id] = token
	_main.set("player_tokens", tokens)

	var viewer_select := _main.get("viewer_select") as OptionButton
	viewer_select.clear()
	viewer_select.add_item(resolved_player_id)
	viewer_select.set_item_metadata(0, resolved_player_id)
	viewer_select.select(0)
	(_main.get("connection_panel") as Control).visible = false
	(_main.get("lobby_panel") as Control).visible = false
	(_main.get("game_panel") as Control).visible = true
	_set_main_status("Attached as %s" % resolved_player_id)
	_main.call_deferred("_refresh_game")
	_reset_stream_session()

func _clear_session() -> void:
	_reset_stream_session()
	if _stream != null:
		_stream.disconnect_stream()
	_main.set("game_id", "")
	_main.set("admin_token", "")
	_main.set("viewer_id", "")
	_main.set("game_state", {})
	_main.set("legal_state", {})
	_main.set("selected_unit_id", "")
	_main.set("selected_settlement_id", "")
	_main.set("selected_tile", Vector2i(999999, 999999))
	_main.set("player_tokens", {})
	var viewer_select := _main.get("viewer_select") as OptionButton
	if viewer_select != null:
		viewer_select.clear()
	var event_log := _main.get("event_log") as RichTextLabel
	if event_log != null:
		event_log.text = ""
	if _attach_token_edit != null:
		_attach_token_edit.clear()
	(_main.get("game_panel") as Control).visible = false
	(_main.get("lobby_panel") as Control).visible = false
	(_main.get("connection_panel") as Control).visible = true
	_set_main_status("Session cleared. Credentials removed from memory.")

func _bootstrap_stream_session(game_id: String, viewer_id: String, token: String) -> void:
	_stream_bootstrap_running = true
	if _stream != null:
		_stream.disconnect_stream(false)
	_session_key = "%s|%s" % [game_id, viewer_id]
	_event_cursor = -1
	_event_history.clear()
	var response := await _api.events(game_id, token, -1)
	if _session_key != "%s|%s" % [str(_main.get("game_id")), str(_main.get("viewer_id"))]:
		_stream_bootstrap_running = false
		return
	if bool(response.get("ok", false)) and response.get("data") is Array:
		for event in response["data"]:
			_merge_event(event)
		_render_event_history()
	else:
		_on_stream_error("initial authorized event sync failed: %s" % response.get("detail", "unknown error"))
	_stream.connect_stream(
		_api.event_websocket_url(game_id, _event_cursor),
		_api.event_websocket_protocols(token)
	)
	_stream_bootstrap_running = false

func _reset_stream_session() -> void:
	_session_key = ""
	_event_cursor = -1
	_event_history.clear()
	_stream_bootstrap_running = false
	if _stream != null:
		_stream.disconnect_stream(false)
	if _stream_status != null:
		_stream_status.text = "Live events: offline"

func _on_stream_event(event: Dictionary) -> void:
	_merge_event(event)
	_render_event_history()
	if not _refresh_pending:
		_refresh_pending = true
		call_deferred("_refresh_projection_after_event")

func _refresh_projection_after_event() -> void:
	_refresh_pending = false
	if _main != null and not str(_main.get("game_id")).is_empty():
		_main.call("_refresh_game")

func _merge_event(event: Variant) -> void:
	if not event is Dictionary:
		return
	var sequence := int(event.get("sequence", -1))
	if sequence <= _event_cursor:
		return
	_event_cursor = sequence
	_event_history.append(event)
	if _event_history.size() > 100:
		_event_history.pop_front()

func _render_event_history() -> void:
	var event_log := _main.get("event_log") as RichTextLabel
	if event_log == null:
		return
	var lines: Array[String] = []
	var start := maxi(0, _event_history.size() - 30)
	for index in range(start, _event_history.size()):
		var event: Dictionary = _event_history[index]
		lines.append("#%s %s %s" % [
			event.get("sequence", "?"),
			event.get("event_type", "?"),
			str(event.get("payload", {})),
		])
	event_log.text = "\n".join(lines) if not lines.is_empty() else "No authorized events"

func _on_stream_status(status: String) -> void:
	if _stream_status != null:
		_stream_status.text = "Live events: %s" % status

func _on_stream_error(message: String) -> void:
	if _stream_status != null:
		_stream_status.tooltip_text = message
	if message.contains("credential was rejected"):
		_set_main_status(message, true)

func _set_main_status(text: String, is_error: bool = false) -> void:
	if _main != null:
		_main.call("_set_status", text, is_error)

func _field_label(text: String) -> Label:
	var label := Label.new()
	label.text = text
	return label

func _find_first_grid(parent: Node) -> GridContainer:
	if parent is GridContainer:
		return parent as GridContainer
	for child in parent.get_children():
		var found := _find_first_grid(child)
		if found != null:
			return found
	return null

func _first_line_edit(parent: Node) -> LineEdit:
	for child in parent.get_children():
		if child is LineEdit:
			return child as LineEdit
		var found := _first_line_edit(child)
		if found != null:
			return found
	return null
