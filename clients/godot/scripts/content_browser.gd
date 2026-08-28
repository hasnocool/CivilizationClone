class_name CivilizationContentBrowser
extends Node

var _main: Node
var _api: CivilizationApiClient
var _catalog: Dictionary = {}
var _civilizations: Array = []
var _unit_by_id: Dictionary = {}
var _building_by_id: Dictionary = {}
var _technology_by_id: Dictionary = {}
var _civilization_by_id: Dictionary = {}
var _research_by_id: Dictionary = {}

var _production_select: OptionButton
var _production_detail: Label
var _technology_select: OptionButton
var _technology_detail: Label
var _civilization_select: OptionButton
var _civilization_detail: Label
var _catalog_status: Label
var _queue_button: Button
var _raw_production_edit: LineEdit

var _catalog_loading := false
var _catalog_loaded_for := ""
var _authorized_refresh_running := false
var _last_authorized_key := ""
var _refresh_requested := false

func _ready() -> void:
	call_deferred("_install")

func _process(_delta: float) -> void:
	if _main == null or _api == null:
		return
	var lobby := _main.get("lobby_panel") as Control
	var game_panel := _main.get("game_panel") as Control
	var connected := (lobby != null and lobby.visible) or (game_panel != null and game_panel.visible)
	if connected and _catalog_loaded_for != _api.base_url and not _catalog_loading:
		_catalog_loading = true
		call_deferred("_load_catalog")

	if game_panel == null or not game_panel.visible:
		return
	var game_id := str(_main.get("game_id"))
	var viewer_id := str(_main.get("viewer_id"))
	var selected_settlement := str(_main.get("selected_settlement_id"))
	var game_state: Dictionary = _main.get("game_state")
	var state_version := int(game_state.get("state_version", -1))
	var kind := _current_production_kind()
	var key := "%s|%s|%s|%d|%s" % [
		game_id,
		viewer_id,
		selected_settlement,
		state_version,
		kind,
	]
	if not game_id.is_empty() and not viewer_id.is_empty() and key != _last_authorized_key:
		_request_authorized_refresh(key)

func _install() -> void:
	_main = get_parent()
	if _main == null:
		return
	_api = _main.get("api") as CivilizationApiClient
	if _api == null:
		return
	_install_production_selector()
	_install_rules_browser()
	_connect_context_signals()
	set_process(true)

func _install_production_selector() -> void:
	_raw_production_edit = _main.get("production_id_edit") as LineEdit
	var kind_select := _main.get("production_kind_select") as OptionButton
	if _raw_production_edit == null or kind_select == null:
		return
	var row := _raw_production_edit.get_parent() as Container
	if row == null:
		return

	_production_select = OptionButton.new()
	_production_select.name = "ProductionChoiceSelect"
	_production_select.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	_production_select.fit_to_longest_item = false
	_production_select.tooltip_text = "Production choices are supplied by the authorized server query."
	_production_select.item_selected.connect(_on_production_selected)
	var insertion_index := _raw_production_edit.get_index()
	row.add_child(_production_select)
	row.move_child(_production_select, insertion_index)

	_raw_production_edit.visible = false
	_raw_production_edit.clear()
	_raw_production_edit.placeholder_text = "server-selected definition id"

	var controls := row.get_parent() as Container
	if controls != null:
		_production_detail = Label.new()
		_production_detail.name = "ProductionChoiceDetail"
		_production_detail.text = "Select one of your settlements to load production choices."
		_production_detail.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
		_production_detail.modulate = Color("94a3b8")
		controls.add_child(_production_detail)
		controls.move_child(_production_detail, mini(row.get_index() + 1, controls.get_child_count() - 1))

	_queue_button = _find_button_by_text(_main, "Queue Production")
	if _queue_button != null:
		_queue_button.disabled = true

func _install_rules_browser() -> void:
	var research_select := _main.get("research_select") as OptionButton
	if research_select == null:
		return
	var controls := research_select.get_parent() as Container
	if controls == null:
		return

	var card := PanelContainer.new()
	card.name = "ContentBrowserCard"
	card.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	var box := VBoxContainer.new()
	box.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	box.add_theme_constant_override("separation", 7)
	card.add_child(box)

	var heading := Label.new()
	heading.text = "Rules Browser"
	heading.add_theme_font_size_override("font_size", 17)
	box.add_child(heading)

	_catalog_status = Label.new()
	_catalog_status.name = "ContentCatalogStatus"
	_catalog_status.text = "Content catalog: connect to server"
	_catalog_status.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	_catalog_status.modulate = Color("94a3b8")
	box.add_child(_catalog_status)

	box.add_child(_field_label("Civilization"))
	_civilization_select = OptionButton.new()
	_civilization_select.name = "CivilizationBrowserSelect"
	_civilization_select.fit_to_longest_item = false
	_civilization_select.item_selected.connect(_on_civilization_selected)
	box.add_child(_civilization_select)
	_civilization_detail = _description_label("Civilization details load from /api/v1/rules/civilizations.")
	_civilization_detail.name = "CivilizationBrowserDetail"
	box.add_child(_civilization_detail)

	box.add_child(_field_label("Technology"))
	_technology_select = OptionButton.new()
	_technology_select.name = "TechnologyBrowserSelect"
	_technology_select.fit_to_longest_item = false
	_technology_select.item_selected.connect(_on_technology_selected)
	box.add_child(_technology_select)
	_technology_detail = _description_label("Technology details load from the server rules catalog.")
	_technology_detail.name = "TechnologyBrowserDetail"
	box.add_child(_technology_detail)

	var insertion_index := maxi(0, research_select.get_index() - 1)
	controls.add_child(card)
	controls.move_child(card, insertion_index)

func _connect_context_signals() -> void:
	var kind_select := _main.get("production_kind_select") as OptionButton
	if kind_select != null:
		kind_select.item_selected.connect(func(_index: int) -> void: _invalidate_authorized_content())
	var settlement_select := _main.get("settlement_select") as OptionButton
	if settlement_select != null:
		settlement_select.item_selected.connect(func(_index: int) -> void: _invalidate_authorized_content())
	var viewer_select := _main.get("viewer_select") as OptionButton
	if viewer_select != null:
		viewer_select.item_selected.connect(func(_index: int) -> void: _invalidate_authorized_content())
	var research_select := _main.get("research_select") as OptionButton
	if research_select != null:
		research_select.item_selected.connect(_on_research_action_selected)

func _load_catalog() -> void:
	var requested_base := _api.base_url
	_catalog_status.text = "Content catalog: loading…"
	var content_response := await _api.rules_content()
	if requested_base != _api.base_url:
		_catalog_loading = false
		return
	if not bool(content_response.get("ok", false)) or not content_response.get("data") is Dictionary:
		_catalog_status.text = "Content catalog unavailable: %s" % content_response.get("detail", "invalid response")
		_catalog_loading = false
		return

	var civ_response := await _api.civilizations()
	if requested_base != _api.base_url:
		_catalog_loading = false
		return
	if not bool(civ_response.get("ok", false)) or not civ_response.get("data") is Array:
		_catalog_status.text = "Civilization catalog unavailable: %s" % civ_response.get("detail", "invalid response")
		_catalog_loading = false
		return

	_catalog = content_response["data"]
	_civilizations = civ_response["data"]
	_reindex_catalog()
	_populate_rules_browser()
	_catalog_loaded_for = requested_base
	_catalog_loading = false
	_catalog_status.text = "Content catalog: server-authoritative"
	_invalidate_authorized_content()

func _reindex_catalog() -> void:
	_unit_by_id.clear()
	_building_by_id.clear()
	_technology_by_id.clear()
	_civilization_by_id.clear()
	for item in _catalog.get("units", []):
		if item is Dictionary:
			_unit_by_id[str(item.get("definition_id", ""))] = item
	for item in _catalog.get("buildings", []):
		if item is Dictionary:
			_building_by_id[str(item.get("definition_id", ""))] = item
	for item in _catalog.get("technologies", []):
		if item is Dictionary:
			_technology_by_id[str(item.get("technology_id", ""))] = item
	for item in _civilizations:
		if item is Dictionary:
			_civilization_by_id[str(item.get("civilization_id", ""))] = item

func _populate_rules_browser() -> void:
	if _civilization_select != null:
		_civilization_select.clear()
		for item in _civilizations:
			if not item is Dictionary:
				continue
			_civilization_select.add_item(str(item.get("name", item.get("civilization_id", "?"))))
			_civilization_select.set_item_metadata(
				_civilization_select.item_count - 1,
				str(item.get("civilization_id", ""))
			)
		if _civilization_select.item_count > 0:
			_civilization_select.select(0)
			_on_civilization_selected(0)

	if _technology_select != null:
		_technology_select.clear()
		for item in _catalog.get("technologies", []):
			if not item is Dictionary:
				continue
			_technology_select.add_item(str(item.get("name", item.get("technology_id", "?"))))
			_technology_select.set_item_metadata(
				_technology_select.item_count - 1,
				str(item.get("technology_id", ""))
			)
		if _technology_select.item_count > 0:
			_technology_select.select(0)
			_on_technology_selected(0)

func _request_authorized_refresh(key: String) -> void:
	if _authorized_refresh_running:
		_refresh_requested = true
		return
	_authorized_refresh_running = true
	_last_authorized_key = key
	call_deferred("_refresh_authorized_content")

func _invalidate_authorized_content() -> void:
	_last_authorized_key = ""
	_refresh_requested = true

func _refresh_authorized_content() -> void:
	var game_id := str(_main.get("game_id"))
	var viewer_id := str(_main.get("viewer_id"))
	var tokens: Dictionary = _main.get("player_tokens")
	var token := str(tokens.get(viewer_id, ""))
	if game_id.is_empty() or viewer_id.is_empty() or token.is_empty():
		_authorized_refresh_running = false
		return

	var research_response := await _api.research_options(game_id, token)
	if bool(research_response.get("ok", false)) and research_response.get("data") is Dictionary:
		_apply_research_options(research_response["data"])
	else:
		_set_catalog_warning("Research options unavailable: %s" % research_response.get("detail", "invalid response"))

	var settlement_id := str(_main.get("selected_settlement_id"))
	if settlement_id.is_empty():
		_clear_production_options("Select one of your settlements to load production choices.")
	else:
		var production_response := await _api.production_options(game_id, token, settlement_id)
		if bool(production_response.get("ok", false)) and production_response.get("data") is Dictionary:
			_apply_production_options(production_response["data"])
		else:
			_clear_production_options("Production options unavailable: %s" % production_response.get("detail", "invalid response"))

	_authorized_refresh_running = false
	if _refresh_requested:
		_refresh_requested = false
		_last_authorized_key = ""

func _apply_research_options(data: Dictionary) -> void:
	_research_by_id.clear()
	for item in data.get("options", []):
		if item is Dictionary:
			_research_by_id[str(item.get("technology_id", ""))] = item

	var research_select := _main.get("research_select") as OptionButton
	if research_select != null:
		var previous := ""
		if research_select.item_count > 0 and research_select.selected >= 0:
			previous = str(research_select.get_item_metadata(research_select.selected))
		research_select.clear()
		var preferred_index := -1
		for item in data.get("options", []):
			if not item is Dictionary or not bool(item.get("selectable", false)):
				continue
			var label := "%s — %s science" % [item.get("name", "?"), item.get("effective_cost", "?")]
			if str(item.get("status", "")) == "selected":
				label += " • selected"
			research_select.add_item(label)
			var index := research_select.item_count - 1
			var technology_id := str(item.get("technology_id", ""))
			research_select.set_item_metadata(index, technology_id)
			if technology_id == previous:
				preferred_index = index
		if research_select.item_count > 0:
			research_select.select(preferred_index if preferred_index >= 0 else 0)
			_on_research_action_selected(research_select.selected)

	if _technology_select != null and _technology_select.item_count > 0:
		_on_technology_selected(_technology_select.selected)

func _apply_production_options(data: Dictionary) -> void:
	if _production_select == null:
		return
	var previous := ""
	if _production_select.item_count > 0 and _production_select.selected >= 0:
		var previous_meta = _production_select.get_item_metadata(_production_select.selected)
		if previous_meta is Dictionary:
			previous = str(previous_meta.get("definition_id", ""))

	_production_select.clear()
	var kind := _current_production_kind()
	var preferred_index := -1
	var first_allowed := -1
	for item in data.get("options", []):
		if not item is Dictionary or str(item.get("kind", "")) != kind:
			continue
		var label := "%s — %s production" % [item.get("name", "?"), item.get("cost", "?")]
		if not bool(item.get("completion_unlocked", true)):
			label += " • future: %s" % _blocker_summary(item.get("completion_blockers", []), item)
		if not bool(item.get("queue_allowed", false)):
			label += " • unavailable"
		_production_select.add_item(label)
		var index := _production_select.item_count - 1
		_production_select.set_item_metadata(index, item)
		var queue_allowed := bool(item.get("queue_allowed", false))
		_production_select.set_item_disabled(index, not queue_allowed)
		if queue_allowed and first_allowed < 0:
			first_allowed = index
		if str(item.get("definition_id", "")) == previous:
			preferred_index = index

	if _production_select.item_count == 0:
		_clear_production_options("No server production definitions are available for this category.")
		return
	var desired := preferred_index if preferred_index >= 0 else first_allowed
	if desired < 0:
		desired = 0
	_production_select.select(desired)
	_on_production_selected(desired)

func _clear_production_options(message: String) -> void:
	if _production_select != null:
		_production_select.clear()
	if _raw_production_edit != null:
		_raw_production_edit.clear()
	if _queue_button != null:
		_queue_button.disabled = true
	if _production_detail != null:
		_production_detail.text = message
		_production_detail.tooltip_text = message

func _on_production_selected(index: int) -> void:
	if _production_select == null or index < 0 or index >= _production_select.item_count:
		return
	var item = _production_select.get_item_metadata(index)
	if not item is Dictionary:
		return
	var definition_id := str(item.get("definition_id", ""))
	if _raw_production_edit != null:
		_raw_production_edit.text = definition_id
	var allowed := bool(item.get("queue_allowed", false))
	if _queue_button != null:
		_queue_button.disabled = not allowed
	var detail := _production_detail_text(item)
	if _production_detail != null:
		_production_detail.text = detail
		_production_detail.tooltip_text = detail
	_production_select.tooltip_text = detail

func _on_research_action_selected(index: int) -> void:
	var research_select := _main.get("research_select") as OptionButton
	if research_select == null or index < 0 or index >= research_select.item_count:
		return
	var technology_id := str(research_select.get_item_metadata(index))
	_select_technology_browser(technology_id)
	var detail := _technology_detail_text(technology_id)
	research_select.tooltip_text = detail

func _on_technology_selected(index: int) -> void:
	if _technology_select == null or index < 0 or index >= _technology_select.item_count:
		return
	var technology_id := str(_technology_select.get_item_metadata(index))
	var detail := _technology_detail_text(technology_id)
	_technology_detail.text = detail
	_technology_select.tooltip_text = detail

func _on_civilization_selected(index: int) -> void:
	if _civilization_select == null or index < 0 or index >= _civilization_select.item_count:
		return
	var civilization_id := str(_civilization_select.get_item_metadata(index))
	var detail := _civilization_detail_text(civilization_id)
	_civilization_detail.text = detail
	_civilization_select.tooltip_text = detail

func _select_technology_browser(technology_id: String) -> void:
	if _technology_select == null:
		return
	for index in range(_technology_select.item_count):
		if str(_technology_select.get_item_metadata(index)) == technology_id:
			_technology_select.select(index)
			_on_technology_selected(index)
			return

func _production_detail_text(option: Dictionary) -> String:
	var definition_id := str(option.get("definition_id", ""))
	var kind := str(option.get("kind", ""))
	var lines: Array[String] = [
		"%s — %s production" % [option.get("name", definition_id), option.get("cost", "?")]
	]
	if kind == "unit":
		var definition: Dictionary = _unit_by_id.get(definition_id, {})
		if not definition.is_empty():
			lines.append("Movement %s • Vision %s • Attack %s • Defense %s" % [
				definition.get("movement", "?"),
				definition.get("vision_radius", "?"),
				definition.get("attack_strength", "?"),
				definition.get("defense_strength", "?"),
			])
			if int(definition.get("ranged_range", 0)) > 0:
				lines.append("Ranged range %s" % definition.get("ranged_range", 0))
			if bool(definition.get("can_found", false)):
				lines.append("Can found settlements")
	else:
		var building: Dictionary = _building_by_id.get(definition_id, {})
		var modifier_parts: Array[String] = []
		for modifier in building.get("yield_modifiers", []):
			if modifier is Dictionary:
				var sign := "+" if int(modifier.get("value", 0)) >= 0 else ""
				modifier_parts.append("%s%s %s" % [sign, modifier.get("value", 0), modifier.get("yield_type", "yield")])
		if not modifier_parts.is_empty():
			lines.append("Yield effect: %s" % ", ".join(modifier_parts))

	if not bool(option.get("completion_unlocked", true)):
		lines.append("Completion gate: %s" % _blocker_summary(option.get("completion_blockers", []), option))
	elif bool(option.get("queue_allowed", false)):
		lines.append("Queue now: allowed • content gates satisfied")
	if not bool(option.get("queue_allowed", false)):
		lines.append("Cannot queue now: %s" % _blocker_summary(option.get("queue_blockers", []), option))
	return "\n".join(lines)

func _technology_detail_text(technology_id: String) -> String:
	var public_definition: Dictionary = _technology_by_id.get(technology_id, {})
	if public_definition.is_empty():
		return technology_id
	var authorized: Dictionary = _research_by_id.get(technology_id, {})
	var lines: Array[String] = [str(public_definition.get("name", technology_id))]
	if authorized.is_empty():
		lines.append("Base cost: %s science" % public_definition.get("cost", "?"))
	else:
		lines.append("Cost: %s science (base %s) • %s" % [
			authorized.get("effective_cost", "?"),
			authorized.get("base_cost", public_definition.get("cost", "?")),
			authorized.get("status", "?"),
		])
	var prerequisites: Array = public_definition.get("prerequisites", [])
	lines.append("Prerequisites: %s" % (_display_id_list(prerequisites) if not prerequisites.is_empty() else "none"))
	var unlocks: Array = public_definition.get("unlocks", [])
	lines.append("Unlocks: %s" % (_display_id_list(unlocks) if not unlocks.is_empty() else "none"))
	if not authorized.is_empty() and not bool(authorized.get("selectable", true)):
		lines.append("Blocked: %s" % _blocker_summary(authorized.get("blockers", []), authorized))
	return "\n".join(lines)

func _civilization_detail_text(civilization_id: String) -> String:
	var civ: Dictionary = _civilization_by_id.get(civilization_id, {})
	if civ.is_empty():
		return civilization_id
	var lines: Array[String] = [
		str(civ.get("name", civilization_id)),
		str(civ.get("description", "")),
	]
	var tags: Array = civ.get("tags", [])
	if not tags.is_empty():
		lines.append("Tags: %s" % ", ".join(tags))
	var resources: Dictionary = civ.get("starting_resources", {})
	var resource_parts: Array[String] = []
	for key in resources.keys():
		resource_parts.append("%s %s" % [resources[key], str(key).capitalize()])
	if not resource_parts.is_empty():
		lines.append("Starting resources: %s" % ", ".join(resource_parts))
	var bonus_parts: Array[String] = []
	for modifier in civ.get("yield_modifiers", []):
		if modifier is Dictionary:
			var sign := "+" if int(modifier.get("value", 0)) >= 0 else ""
			bonus_parts.append("%s%s %s" % [sign, modifier.get("value", 0), modifier.get("yield_type", "yield")])
	var research_percent := int(civ.get("research_cost_percent", 0))
	if research_percent != 0:
		bonus_parts.append("%+d%% research cost" % research_percent)
	var attack_percent := int(civ.get("attack_strength_percent", 0))
	if attack_percent != 0:
		bonus_parts.append("%+d%% attack" % attack_percent)
	var defense_percent := int(civ.get("defense_strength_percent", 0))
	if defense_percent != 0:
		bonus_parts.append("%+d%% defense" % defense_percent)
	if not bonus_parts.is_empty():
		lines.append("Bonuses: %s" % ", ".join(bonus_parts))
	var unique_units: Array = civ.get("unique_units", [])
	var unique_buildings: Array = civ.get("unique_buildings", [])
	if not unique_units.is_empty():
		lines.append("Unique units: %s" % _display_id_list(unique_units))
	if not unique_buildings.is_empty():
		lines.append("Unique buildings: %s" % _display_id_list(unique_buildings))
	return "\n".join(lines)

func _blocker_summary(blockers: Variant, context: Dictionary) -> String:
	if not blockers is Array or blockers.is_empty():
		return "none"
	var parts: Array[String] = []
	for blocker in blockers:
		match str(blocker):
			"civilization_restricted":
				var civilization_id := str(context.get("required_civilization", ""))
				parts.append("requires %s" % _civilization_name(civilization_id))
			"technology_required":
				var technology_id := str(context.get("required_technology", ""))
				parts.append("requires %s" % _content_name(technology_id))
			"prerequisites_incomplete":
				parts.append("prerequisites incomplete")
			"already_completed":
				parts.append("already completed")
			"already_built":
				parts.append("already built")
			"not_active_player":
				parts.append("not the active player")
			_:
				parts.append(str(blocker).replace("_", " "))
	return ", ".join(parts)

func _display_id_list(values: Array) -> String:
	var names: Array[String] = []
	for value in values:
		names.append(_content_name(str(value)))
	return ", ".join(names)

func _content_name(content_id: String) -> String:
	if _unit_by_id.has(content_id):
		return str((_unit_by_id[content_id] as Dictionary).get("name", content_id))
	if _building_by_id.has(content_id):
		return str((_building_by_id[content_id] as Dictionary).get("name", content_id))
	if _technology_by_id.has(content_id):
		return str((_technology_by_id[content_id] as Dictionary).get("name", content_id))
	return content_id.replace("_", " ").capitalize()

func _civilization_name(civilization_id: String) -> String:
	if _civilization_by_id.has(civilization_id):
		return str((_civilization_by_id[civilization_id] as Dictionary).get("name", civilization_id))
	return civilization_id.replace("_", " ").capitalize()

func _current_production_kind() -> String:
	var kind_select := _main.get("production_kind_select") as OptionButton
	if kind_select == null or kind_select.item_count == 0:
		return "unit"
	return kind_select.get_item_text(kind_select.selected)

func _set_catalog_warning(message: String) -> void:
	if _catalog_status != null:
		_catalog_status.text = message

func _field_label(text: String) -> Label:
	var label := Label.new()
	label.text = text
	return label

func _description_label(text: String) -> Label:
	var label := Label.new()
	label.text = text
	label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	label.modulate = Color("94a3b8")
	return label

func _find_button_by_text(parent: Node, text: String) -> Button:
	if parent is Button and (parent as Button).text == text:
		return parent as Button
	for child in parent.get_children():
		var found := _find_button_by_text(child, text)
		if found != null:
			return found
	return null
