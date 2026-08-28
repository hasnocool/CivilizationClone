extends SceneTree

func _init() -> void:
	var packed := load("res://scenes/main.tscn") as PackedScene
	if packed == null:
		_fail("Could not load main.tscn")
		return
	var instance := packed.instantiate()
	if instance == null:
		_fail("Could not instantiate main scene")
		return
	root.add_child(instance)
	await process_frame
	await process_frame
	await process_frame
	await process_frame
	var main := root.get_node_or_null("Main")
	if main == null:
		_fail("Main scene did not enter the tree")
		return
	if not bool(ProjectSettings.get_setting("display/window/size/resizable", false)):
		_fail("Godot client window must remain resizable")
		return
	if _find_first(main, "ResponsiveGameSplit") == null:
		_fail("Responsive game split was not installed")
		return
	if _find_first(main, "ClientToolbar") == null:
		_fail("Client toolbar was not installed")
		return
	var settings := _find_first(main, "SettingsScreen") as CivilizationSettingsScreen
	if settings == null:
		_fail("Display settings screen was not installed")
		return
	if settings.visible:
		_fail("Settings screen should be hidden on normal startup")
		return
	if settings.resolution_select == null or settings.resolution_select.item_count < 6:
		_fail("Settings screen does not expose enough resolution choices")
		return
	if settings.mode_select == null or settings.mode_select.item_count < 4:
		_fail("Settings screen does not expose window modes")
		return
	if settings.ui_scale_select == null or settings.ui_scale_select.item_count < 5:
		_fail("Settings screen does not expose UI scale choices")
		return
	if _contains_hsplit(main):
		_fail("Fixed horizontal split remained after responsive installation")
		return
	if _contains_hbox(main):
		_fail("Fixed horizontal row remained after responsive installation")
		return
	if _count_named(main, "SidebarCard") < 5:
		_fail("Gameplay sidebar sections were not grouped into visible cards")
		return
	var map := _find_map(main)
	if map == null:
		_fail("Hex map was not created")
		return
	if map.custom_minimum_size.x > 320.0 or map.custom_minimum_size.y > 280.0:
		_fail("Hex map retains an oversized fixed minimum")
		return
	if not _dropdowns_are_responsive(main):
		_fail("One or more dropdowns still reserve width for their longest item")
		return
	if not _visual_hierarchy_is_distinct(main, settings):
		_fail("Buttons, field controls, headings, and descriptions are not visually distinct")
		return
	if not _complete_api_surface_is_installed(main):
		_fail("Complete v1 API controls were not installed")
		return

	main.call("_rebuild_player_rows")
	await process_frame
	await process_frame
	await process_frame
	if _count_named(main, "ControllerSelect") < 2:
		_fail("Dynamically-created player rows do not expose Human/Bot controller selection")
		return

	var api := main.get("api") as CivilizationApiClient
	if api == null:
		_fail("API client is unavailable")
		return
	var token := "smoke-secret-token"
	var ws_url := api.event_websocket_url("game-one", 12)
	if ws_url.contains(token) or not ws_url.contains("after_sequence=12"):
		_fail("WebSocket URL resume/credential handling is unsafe")
		return
	var protocols := api.event_websocket_protocols(token)
	if protocols.size() != 2 or protocols[0] != "civilization.v1" or protocols[1] != token:
		_fail("WebSocket credential subprotocol contract is incorrect")
		return

	print("GODOT CLIENT SMOKE PASS")
	quit(0)

func _find_first(parent: Node, target_name: String) -> Node:
	if parent.name == target_name:
		return parent
	for child in parent.get_children():
		var found := _find_first(child, target_name)
		if found != null:
			return found
	return null

func _count_named(parent: Node, target_name: String) -> int:
	var count := 1 if parent.name == target_name else 0
	for child in parent.get_children():
		count += _count_named(child, target_name)
	return count

func _contains_hsplit(parent: Node) -> bool:
	for child in parent.get_children():
		if child is HSplitContainer:
			return true
		if _contains_hsplit(child):
			return true
	return false

func _contains_hbox(parent: Node) -> bool:
	for child in parent.get_children():
		if child is HBoxContainer:
			return true
		if _contains_hbox(child):
			return true
	return false

func _dropdowns_are_responsive(parent: Node) -> bool:
	if parent is OptionButton:
		var option := parent as OptionButton
		if option.fit_to_longest_item:
			return false
		if option.custom_minimum_size.x > 0.0:
			return false
	for child in parent.get_children():
		if not _dropdowns_are_responsive(child):
			return false
	return true

func _visual_hierarchy_is_distinct(main: Node, settings: CivilizationSettingsScreen) -> bool:
	var connect_button := _find_button_by_text(main, "Connect")
	if connect_button == null or not connect_button.has_theme_stylebox_override("normal"):
		return false
	if settings.mode_select == null or not settings.mode_select.has_theme_stylebox_override("normal"):
		return false
	var title := _find_label_by_text(main, "CivilizationClone — Godot Client")
	var section := _find_label_by_text(main, "Research")
	var description := _find_label_prefix(main, "Selection:")
	if title == null or section == null or description == null:
		return false
	var title_color := title.get_theme_color("font_color")
	var section_color := section.get_theme_color("font_color")
	var description_color := description.get_theme_color("font_color")
	return title_color != section_color and section_color != description_color and title_color != description_color

func _complete_api_surface_is_installed(main: Node) -> bool:
	if _find_first(main, "ApiFeatures") == null:
		return false
	if _find_first(main, "AuthorizedEventStream") == null:
		return false
	if _find_first(main, "WaterPercentSpin") == null or _find_first(main, "ResourcePercentSpin") == null:
		return false
	if _find_first(main, "AttachExistingButton") == null:
		return false
	var token_edit := _find_first(main, "AttachPlayerTokenEdit") as LineEdit
	if token_edit == null or not token_edit.secret:
		return false
	if _find_first(main, "LiveEventStatus") == null:
		return false
	if _find_first(main, "ClearSessionButton") == null:
		return false
	return true

func _find_button_by_text(parent: Node, text: String) -> Button:
	if parent is Button and (parent as Button).text == text:
		return parent as Button
	for child in parent.get_children():
		var found := _find_button_by_text(child, text)
		if found != null:
			return found
	return null

func _find_label_by_text(parent: Node, text: String) -> Label:
	if parent is Label and (parent as Label).text == text:
		return parent as Label
	for child in parent.get_children():
		var found := _find_label_by_text(child, text)
		if found != null:
			return found
	return null

func _find_label_prefix(parent: Node, prefix: String) -> Label:
	if parent is Label and (parent as Label).text.begins_with(prefix):
		return parent as Label
	for child in parent.get_children():
		var found := _find_label_prefix(child, prefix)
		if found != null:
			return found
	return null

func _find_map(parent: Node) -> CivilizationHexMap:
	for child in parent.get_children():
		if child is CivilizationHexMap:
			return child as CivilizationHexMap
		var found := _find_map(child)
		if found != null:
			return found
	return null

func _fail(message: String) -> void:
	push_error(message)
	quit(1)
