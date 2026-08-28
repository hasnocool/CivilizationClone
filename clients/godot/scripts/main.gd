extends Control

var api: CivilizationApiClient
var civilization_defs: Array = []
var player_rows: Array[Dictionary] = []
var player_tokens: Dictionary = {}
var game_id: String = ""
var admin_token: String = ""
var viewer_id: String = ""
var game_state: Dictionary = {}
var legal_state: Dictionary = {}
var selected_unit_id: String = ""
var selected_settlement_id: String = ""
var selected_tile := Vector2i(999999, 999999)

var status_label: Label
var connection_panel: Control
var lobby_panel: Control
var game_panel: Control
var api_url_edit: LineEdit
var game_id_edit: LineEdit
var seed_spin: SpinBox
var player_count_spin: SpinBox
var map_radius_spin: SpinBox
var player_config_box: VBoxContainer
var viewer_select: OptionButton
var game_info_label: Label
var selection_label: Label
var legal_label: Label
var research_select: OptionButton
var settlement_select: OptionButton
var production_kind_select: OptionButton
var production_id_edit: LineEdit
var diplomacy_select: OptionButton
var event_log: RichTextLabel
var hex_map: CivilizationHexMap

func _ready() -> void:
	api = CivilizationApiClient.new()
	add_child(api)
	_build_ui()

func _build_ui() -> void:
	var margin := MarginContainer.new()
	margin.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	margin.add_theme_constant_override("margin_left", 14)
	margin.add_theme_constant_override("margin_right", 14)
	margin.add_theme_constant_override("margin_top", 12)
	margin.add_theme_constant_override("margin_bottom", 12)
	add_child(margin)

	var root := VBoxContainer.new()
	root.add_theme_constant_override("separation", 10)
	margin.add_child(root)

	var title := Label.new()
	title.text = "CivilizationClone — Godot Client"
	title.add_theme_font_size_override("font_size", 24)
	root.add_child(title)

	status_label = Label.new()
	status_label.text = "Disconnected"
	status_label.modulate = Color("b8c2cf")
	root.add_child(status_label)

	connection_panel = _build_connection_panel()
	root.add_child(connection_panel)
	lobby_panel = _build_lobby_panel()
	lobby_panel.visible = false
	root.add_child(lobby_panel)
	game_panel = _build_game_panel()
	game_panel.visible = false
	game_panel.size_flags_vertical = Control.SIZE_EXPAND_FILL
	root.add_child(game_panel)

func _build_connection_panel() -> Control:
	var panel := PanelContainer.new()
	var row := HBoxContainer.new()
	row.add_theme_constant_override("separation", 8)
	panel.add_child(row)
	row.add_child(_label("API"))
	api_url_edit = LineEdit.new()
	api_url_edit.text = "http://127.0.0.1:8000"
	api_url_edit.placeholder_text = "http://127.0.0.1:8000"
	api_url_edit.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	row.add_child(api_url_edit)
	var connect_button := _button("Connect")
	connect_button.pressed.connect(_connect_api)
	row.add_child(connect_button)
	return panel

func _build_lobby_panel() -> Control:
	var panel := PanelContainer.new()
	var box := VBoxContainer.new()
	box.add_theme_constant_override("separation", 8)
	panel.add_child(box)

	var parameters := GridContainer.new()
	parameters.columns = 4
	parameters.add_theme_constant_override("h_separation", 8)
	parameters.add_theme_constant_override("v_separation", 6)
	box.add_child(parameters)

	parameters.add_child(_label("Game ID"))
	game_id_edit = LineEdit.new()
	game_id_edit.text = "godot-game"
	parameters.add_child(game_id_edit)
	parameters.add_child(_label("Seed"))
	seed_spin = SpinBox.new()
	seed_spin.min_value = 0
	seed_spin.max_value = 2147483647
	seed_spin.value = 1
	parameters.add_child(seed_spin)
	parameters.add_child(_label("Players"))
	player_count_spin = SpinBox.new()
	player_count_spin.min_value = 2
	player_count_spin.max_value = 4
	player_count_spin.step = 1
	player_count_spin.value = 2
	player_count_spin.value_changed.connect(_on_player_count_changed)
	parameters.add_child(player_count_spin)
	parameters.add_child(_label("Map radius"))
	map_radius_spin = SpinBox.new()
	map_radius_spin.min_value = 3
	map_radius_spin.max_value = 10
	map_radius_spin.step = 1
	map_radius_spin.value = 4
	parameters.add_child(map_radius_spin)

	var heading := Label.new()
	heading.text = "Hotseat players"
	heading.add_theme_font_size_override("font_size", 18)
	box.add_child(heading)
	player_config_box = VBoxContainer.new()
	box.add_child(player_config_box)

	var start_button := _button("Create & Start Game")
	start_button.pressed.connect(_create_and_start_game)
	box.add_child(start_button)
	return panel

func _build_game_panel() -> Control:
	var outer := VBoxContainer.new()
	outer.add_theme_constant_override("separation", 8)

	var top := HBoxContainer.new()
	outer.add_child(top)
	viewer_select = OptionButton.new()
	viewer_select.item_selected.connect(_on_viewer_selected)
	viewer_select.custom_minimum_size.x = 180
	top.add_child(_label("Viewer"))
	top.add_child(viewer_select)
	var refresh_button := _button("Refresh")
	refresh_button.pressed.connect(_refresh_game)
	top.add_child(refresh_button)
	game_info_label = Label.new()
	game_info_label.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	game_info_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT
	top.add_child(game_info_label)

	var split := HSplitContainer.new()
	split.size_flags_vertical = Control.SIZE_EXPAND_FILL
	split.split_offset = 870
	outer.add_child(split)

	hex_map = CivilizationHexMap.new()
	hex_map.custom_minimum_size = Vector2(760, 620)
	hex_map.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	hex_map.size_flags_vertical = Control.SIZE_EXPAND_FILL
	hex_map.tile_clicked.connect(_on_map_tile_clicked)
	split.add_child(hex_map)

	var scroll := ScrollContainer.new()
	scroll.custom_minimum_size.x = 390
	scroll.size_flags_vertical = Control.SIZE_EXPAND_FILL
	split.add_child(scroll)
	var controls := VBoxContainer.new()
	controls.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	controls.add_theme_constant_override("separation", 7)
	scroll.add_child(controls)

	selection_label = _label("Selection: none")
	selection_label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	controls.add_child(selection_label)

	var found_button := _button("Found Settlement (selected unit)")
	found_button.pressed.connect(_found_settlement)
	controls.add_child(found_button)

	controls.add_child(_section("Research"))
	research_select = OptionButton.new()
	controls.add_child(research_select)
	var research_button := _button("Choose Research")
	research_button.pressed.connect(_choose_research)
	controls.add_child(research_button)

	controls.add_child(_section("Settlement / Production"))
	settlement_select = OptionButton.new()
	settlement_select.item_selected.connect(_on_settlement_selected)
	controls.add_child(settlement_select)
	var tile_row := HBoxContainer.new()
	var work_button := _button("Work selected tile")
	work_button.pressed.connect(func() -> void: await _set_worked_tile(true))
	tile_row.add_child(work_button)
	var unwork_button := _button("Unwork selected tile")
	unwork_button.pressed.connect(func() -> void: await _set_worked_tile(false))
	tile_row.add_child(unwork_button)
	controls.add_child(tile_row)

	var production_row := HBoxContainer.new()
	production_kind_select = OptionButton.new()
	production_kind_select.add_item("unit")
	production_kind_select.add_item("building")
	production_row.add_child(production_kind_select)
	production_id_edit = LineEdit.new()
	production_id_edit.placeholder_text = "definition id (server validates)"
	production_id_edit.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	production_row.add_child(production_id_edit)
	controls.add_child(production_row)
	var queue_button := _button("Queue Production")
	queue_button.pressed.connect(_queue_production)
	controls.add_child(queue_button)
	var cancel_button := _button("Cancel First Queue Item")
	cancel_button.pressed.connect(_cancel_production)
	controls.add_child(cancel_button)

	controls.add_child(_section("Diplomacy"))
	diplomacy_select = OptionButton.new()
	controls.add_child(diplomacy_select)
	var diplomacy_grid := GridContainer.new()
	diplomacy_grid.columns = 2
	for definition in [
		["Declare War", "DeclareWar"],
		["Offer Peace", "OfferPeace"],
		["Accept Peace", "AcceptPeace"],
		["Reject Peace", "RejectPeace"],
	]:
		var action_button := _button(definition[0])
		var command_type: String = definition[1]
		action_button.pressed.connect(func() -> void: await _diplomacy_command(command_type))
		diplomacy_grid.add_child(action_button)
	controls.add_child(diplomacy_grid)

	controls.add_child(_section("Turn"))
	var turn_row := HBoxContainer.new()
	var end_button := _button("End Turn")
	end_button.pressed.connect(func() -> void: await _submit_command("EndTurn", {}))
	turn_row.add_child(end_button)
	var concede_button := _button("Concede")
	concede_button.pressed.connect(func() -> void: await _submit_command("Concede", {}))
	turn_row.add_child(concede_button)
	controls.add_child(turn_row)

	legal_label = Label.new()
	legal_label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	controls.add_child(legal_label)
	controls.add_child(_section("Authorized Events"))
	event_log = RichTextLabel.new()
	event_log.fit_content = false
	event_log.custom_minimum_size = Vector2(340, 220)
	event_log.scroll_active = true
	controls.add_child(event_log)
	return outer

func _connect_api() -> void:
	_set_status("Connecting…")
	api.configure(api_url_edit.text)
	var health_response := await api.health()
	if not _response_ok(health_response, "Health check failed"):
		return
	var civ_response := await api.civilizations()
	if not _response_ok(civ_response, "Could not load civilizations"):
		return
	if not civ_response["data"] is Array:
		_set_status("Civilization catalog is not an array", true)
		return
	civilization_defs = civ_response["data"]
	connection_panel.visible = false
	lobby_panel.visible = true
	_rebuild_player_rows()
	_set_status("Connected. Configure a new hotseat game.")

func _on_player_count_changed(_value: float) -> void:
	_rebuild_player_rows()

func _rebuild_player_rows() -> void:
	if player_config_box == null:
		return
	for child in player_config_box.get_children():
		player_config_box.remove_child(child)
		child.queue_free()
	player_rows.clear()
	for index in range(int(player_count_spin.value)):
		var row := HBoxContainer.new()
		var player_id_edit := LineEdit.new()
		player_id_edit.text = "p%d" % (index + 1)
		player_id_edit.custom_minimum_size.x = 90
		row.add_child(player_id_edit)
		var player_name_edit := LineEdit.new()
		player_name_edit.text = "Player %d" % (index + 1)
		player_name_edit.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		row.add_child(player_name_edit)
		var civilization_select := OptionButton.new()
		civilization_select.custom_minimum_size.x = 190
		for civ_index in range(civilization_defs.size()):
			var civ: Dictionary = civilization_defs[civ_index]
			civilization_select.add_item(str(civ.get("name", civ.get("civilization_id", "?"))))
			civilization_select.set_item_metadata(civ_index, str(civ.get("civilization_id", "")))
		if civilization_select.item_count > 0:
			civilization_select.select(index % civilization_select.item_count)
		row.add_child(civilization_select)
		player_config_box.add_child(row)
		player_rows.append({
			"id": player_id_edit,
			"name": player_name_edit,
			"civilization": civilization_select,
		})

func _create_and_start_game() -> void:
	var requested_game_id := game_id_edit.text.strip_edges()
	if requested_game_id.is_empty():
		_set_status("Game ID is required", true)
		return
	_set_status("Creating game…")
	var created := await api.create_game(
		requested_game_id,
		int(seed_spin.value),
		int(player_count_spin.value),
		int(map_radius_spin.value)
	)
	if not _response_ok(created, "Create game failed"):
		return
	var created_data: Dictionary = created["data"]
	game_id = str(created_data.get("game_id", requested_game_id))
	admin_token = str(created_data.get("admin_token", ""))
	if admin_token.is_empty():
		_set_status("Server did not return an admin credential", true)
		return

	player_tokens.clear()
	for row in player_rows:
		var player_id_value := (row["id"] as LineEdit).text.strip_edges()
		var player_name_value := (row["name"] as LineEdit).text.strip_edges()
		var civilization_select := row["civilization"] as OptionButton
		var civilization_id := str(civilization_select.get_item_metadata(civilization_select.selected))
		var joined := await api.join_player(
			game_id,
			admin_token,
			player_id_value,
			player_name_value,
			civilization_id
		)
		if not _response_ok(joined, "Player enrollment failed"):
			return
		var join_data: Dictionary = joined["data"]
		if not bool(join_data.get("accepted", false)):
			_set_status(_feedback_text(join_data), true)
			return
		var token := str(join_data.get("player_token", ""))
		if token.is_empty():
			_set_status("Server did not return a player credential", true)
			return
		player_tokens[player_id_value] = token

	var started := await api.start_game(game_id, admin_token)
	if not _response_ok(started, "Start game failed"):
		return
	var started_data: Dictionary = started["data"]
	if not bool(started_data.get("accepted", false)):
		_set_status(_feedback_text(started_data), true)
		return

	lobby_panel.visible = false
	game_panel.visible = true
	viewer_select.clear()
	for player_id_value in player_tokens.keys():
		viewer_select.add_item(str(player_id_value))
		viewer_select.set_item_metadata(viewer_select.item_count - 1, str(player_id_value))
	viewer_select.select(0)
	viewer_id = str(viewer_select.get_item_metadata(0))
	_set_status("Game started")
	await _refresh_game()

func _on_viewer_selected(index: int) -> void:
	if index < 0 or index >= viewer_select.item_count:
		return
	viewer_id = str(viewer_select.get_item_metadata(index))
	selected_unit_id = ""
	selected_settlement_id = ""
	if is_inside_tree():
		await _refresh_game()

func _refresh_game() -> void:
	if game_id.is_empty() or viewer_id.is_empty():
		return
	var token := str(player_tokens.get(viewer_id, ""))
	if token.is_empty():
		_set_status("No credential for viewer %s" % viewer_id, true)
		return

	var state_response := await api.state(game_id, token)
	if not _response_ok(state_response, "State refresh failed"):
		return
	var legal_response := await api.legal_actions(game_id, token)
	if not _response_ok(legal_response, "Legal-action refresh failed"):
		return
	var events_response := await api.events(game_id, token)
	if not _response_ok(events_response, "Event refresh failed"):
		return

	game_state = state_response["data"]
	legal_state = legal_response["data"]
	hex_map.set_state(game_state)
	hex_map.set_selected_unit(selected_unit_id)
	_update_game_info()
	_update_selection_controls()
	_update_research_options()
	_update_settlement_options()
	_update_diplomacy_options()
	_update_legal_actions()
	_update_events(events_response["data"])

func _on_map_tile_clicked(q: int, r: int) -> void:
	selected_tile = Vector2i(q, r)
	var viewer := str(game_state.get("viewer", {}).get("player_id", ""))
	for raw_unit in game_state.get("units", []):
		if raw_unit is Dictionary and int(raw_unit.get("q", 0)) == q and int(raw_unit.get("r", 0)) == r:
			if str(raw_unit.get("owner_id", "")) == viewer:
				selected_unit_id = str(raw_unit.get("unit_id", ""))
				hex_map.set_selected_unit(selected_unit_id)
				_update_selection_controls()
				return
			if not selected_unit_id.is_empty():
				await _submit_command(
					"AttackUnit",
					{"attacker_id": selected_unit_id, "defender_id": str(raw_unit.get("unit_id", ""))}
				)
				return

	for raw_settlement in game_state.get("settlements", []):
		if raw_settlement is Dictionary and int(raw_settlement.get("q", 0)) == q and int(raw_settlement.get("r", 0)) == r:
			if str(raw_settlement.get("owner_id", "")) == viewer:
				selected_settlement_id = str(raw_settlement.get("settlement_id", ""))
				_select_settlement_option(selected_settlement_id)
				_update_selection_controls()
				return

	if not selected_unit_id.is_empty():
		await _submit_command("MoveUnit", {"unit_id": selected_unit_id, "q": q, "r": r})

func _found_settlement() -> void:
	if selected_unit_id.is_empty():
		_set_status("Select one of your units first", true)
		return
	await _submit_command("FoundSettlement", {"unit_id": selected_unit_id})

func _choose_research() -> void:
	if research_select.item_count == 0:
		_set_status("No selectable research is currently exposed", true)
		return
	var technology_id := str(research_select.get_item_metadata(research_select.selected))
	await _submit_command("ChooseResearch", {"technology_id": technology_id})

func _queue_production() -> void:
	var settlement_id := _current_settlement_id()
	var definition_id := production_id_edit.text.strip_edges()
	if settlement_id.is_empty() or definition_id.is_empty():
		_set_status("Choose a settlement and enter a server definition id", true)
		return
	await _submit_command(
		"QueueProduction",
		{
			"settlement_id": settlement_id,
			"kind": production_kind_select.get_item_text(production_kind_select.selected),
			"definition_id": definition_id,
		}
	)

func _cancel_production() -> void:
	var settlement_id := _current_settlement_id()
	if settlement_id.is_empty():
		_set_status("Choose a settlement first", true)
		return
	await _submit_command("CancelProduction", {"settlement_id": settlement_id, "index": 0})

func _set_worked_tile(worked: bool) -> void:
	var settlement_id := _current_settlement_id()
	if settlement_id.is_empty() or selected_tile.x == 999999:
		_set_status("Choose a settlement and map tile first", true)
		return
	await _submit_command(
		"SetWorkedTile",
		{
			"settlement_id": settlement_id,
			"q": selected_tile.x,
			"r": selected_tile.y,
			"worked": worked,
		}
	)

func _diplomacy_command(command_type: String) -> void:
	if diplomacy_select.item_count == 0:
		_set_status("No diplomacy target available", true)
		return
	var target := str(diplomacy_select.get_item_metadata(diplomacy_select.selected))
	await _submit_command(command_type, {"target_player_id": target})

func _submit_command(command_type: String, payload: Dictionary) -> void:
	if game_state.is_empty():
		return
	var token := str(player_tokens.get(viewer_id, ""))
	var response := await api.command(
		game_id,
		token,
		command_type,
		viewer_id,
		int(game_state.get("state_version", -1)),
		payload
	)
	if not _response_ok(response, "%s failed" % command_type):
		return
	var data: Dictionary = response["data"]
	if bool(data.get("accepted", false)):
		_set_status("Accepted: %s" % command_type)
		if command_type in ["MoveUnit", "AttackUnit", "FoundSettlement"]:
			selected_unit_id = ""
	else:
		_set_status(_feedback_text(data), true)
	await _refresh_game()

func _update_game_info() -> void:
	var viewer: Dictionary = game_state.get("viewer", {})
	var research: Dictionary = viewer.get("research", {})
	game_info_label.text = (
		"Turn %s | active %s | %s | G %s S %s C %s | research %s"
		% [
			game_state.get("turn", "?"),
			game_state.get("active_player_id", "-"),
			viewer.get("civilization_id", "-"),
			viewer.get("gold", 0),
			viewer.get("science", 0),
			viewer.get("culture", 0),
			research.get("selected", "-") if research.get("selected") != null else "-",
		]
	)

func _update_selection_controls() -> void:
	var parts: Array[String] = []
	if not selected_unit_id.is_empty():
		parts.append("unit %s" % selected_unit_id)
	if not selected_settlement_id.is_empty():
		parts.append("settlement %s" % selected_settlement_id)
	if selected_tile.x != 999999:
		parts.append("tile (%d,%d)" % [selected_tile.x, selected_tile.y])
	selection_label.text = "Selection: %s" % (", ".join(parts) if not parts.is_empty() else "none")

func _update_research_options() -> void:
	research_select.clear()
	var viewer: Dictionary = game_state.get("viewer", {})
	var research: Dictionary = viewer.get("research", {})
	var options: Array = research.get("available", [])
	if options.is_empty():
		for decision in legal_state.get("mandatory_decisions", []):
			if decision is Dictionary and str(decision.get("kind", "")) == "research":
				options = decision.get("options", [])
	for technology in options:
		research_select.add_item(str(technology))
		research_select.set_item_metadata(research_select.item_count - 1, str(technology))

func _update_settlement_options() -> void:
	var previous := selected_settlement_id
	settlement_select.clear()
	var viewer := str(game_state.get("viewer", {}).get("player_id", ""))
	for raw in game_state.get("settlements", []):
		if raw is Dictionary and str(raw.get("owner_id", "")) == viewer:
			var settlement_id := str(raw.get("settlement_id", ""))
			settlement_select.add_item(settlement_id)
			settlement_select.set_item_metadata(settlement_select.item_count - 1, settlement_id)
	if settlement_select.item_count > 0:
		var desired := previous
		if desired.is_empty():
			desired = str(settlement_select.get_item_metadata(0))
		_select_settlement_option(desired)
	else:
		selected_settlement_id = ""

func _on_settlement_selected(index: int) -> void:
	if index >= 0 and index < settlement_select.item_count:
		selected_settlement_id = str(settlement_select.get_item_metadata(index))
		_update_selection_controls()

func _select_settlement_option(settlement_id: String) -> void:
	for index in range(settlement_select.item_count):
		if str(settlement_select.get_item_metadata(index)) == settlement_id:
			settlement_select.select(index)
			selected_settlement_id = settlement_id
			return

func _current_settlement_id() -> String:
	if settlement_select.item_count == 0:
		return ""
	return str(settlement_select.get_item_metadata(settlement_select.selected))

func _update_diplomacy_options() -> void:
	diplomacy_select.clear()
	for relation in game_state.get("diplomacy", []):
		if relation is Dictionary:
			var target := str(relation.get("other_player_id", ""))
			var status := str(relation.get("status", "?"))
			diplomacy_select.add_item("%s (%s)" % [target, status])
			diplomacy_select.set_item_metadata(diplomacy_select.item_count - 1, target)

func _update_legal_actions() -> void:
	var actions: Array = legal_state.get("actions", [])
	var mandatory: Array = legal_state.get("mandatory_decisions", [])
	legal_label.text = "Legal: %s\nMandatory: %s" % [", ".join(actions), str(mandatory)]

func _update_events(events: Variant) -> void:
	if not events is Array:
		event_log.text = "No event data"
		return
	var lines: Array[String] = []
	var start := maxi(0, events.size() - 30)
	for index in range(start, events.size()):
		var event = events[index]
		if event is Dictionary:
			lines.append(
				"#%s %s %s" % [
					event.get("sequence", "?"),
					event.get("event_type", "?"),
					str(event.get("payload", {})),
				]
			)
	event_log.text = "\n".join(lines) if not lines.is_empty() else "No authorized events"

func _response_ok(response: Dictionary, prefix: String) -> bool:
	if bool(response.get("ok", false)):
		return true
	_set_status("%s: %s" % [prefix, response.get("detail", "unknown error")], true)
	return false

func _feedback_text(data: Dictionary) -> String:
	var feedback: Array = data.get("feedback", [])
	if feedback.is_empty():
		return "Command rejected"
	var lines: Array[String] = []
	for item in feedback:
		if item is Dictionary:
			lines.append("%s: %s" % [item.get("code", "ERROR"), item.get("message", "")])
	return " | ".join(lines)

func _set_status(text: String, is_error: bool = false) -> void:
	status_label.text = text
	status_label.modulate = Color("ff8a80") if is_error else Color("b8c2cf")

func _label(text: String) -> Label:
	var value := Label.new()
	value.text = text
	return value

func _section(text: String) -> Label:
	var value := Label.new()
	value.text = text
	value.add_theme_font_size_override("font_size", 17)
	return value

func _button(text: String) -> Button:
	var value := Button.new()
	value.text = text
	return value
