class_name CivilizationUiShell
extends Node

const SettingsScreen := preload("res://scripts/settings_screen.gd")
const PANEL_BG := Color("151b24")
const PANEL_BORDER := Color("334155")
const CONTROL_HEIGHT := 36.0
const CONFIGURED_META := &"civilization_ui_shell_configured"

var _root_control: Control
var _settings: CivilizationSettingsScreen
var _display_label: Label
var _normalization_pending: Dictionary = {}

func _ready() -> void:
	call_deferred("_install")

func _exit_tree() -> void:
	if get_tree() != null and get_tree().node_added.is_connected(_on_node_added):
		get_tree().node_added.disconnect(_on_node_added)
	if get_viewport() != null and get_viewport().size_changed.is_connected(_on_viewport_changed):
		get_viewport().size_changed.disconnect(_on_viewport_changed)

func _install() -> void:
	_root_control = get_parent() as Control
	if _root_control == null:
		return
	_build_toolbar()
	_normalize_subtree(_root_control)
	_settings = SettingsScreen.new()
	_settings.name = "SettingsScreen"
	_root_control.add_child(_settings)
	_settings.settings_applied.connect(_on_settings_applied)
	get_tree().node_added.connect(_on_node_added)
	get_viewport().size_changed.connect(_on_viewport_changed)
	_on_viewport_changed()

func _build_toolbar() -> void:
	var root_box := _find_primary_vbox(_root_control)
	if root_box == null:
		return

	var toolbar := HFlowContainer.new()
	toolbar.name = "ClientToolbar"
	toolbar.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	toolbar.add_theme_constant_override("h_separation", 8)
	toolbar.add_theme_constant_override("v_separation", 6)

	var menu := MenuButton.new()
	menu.text = "Menu"
	menu.custom_minimum_size.y = CONTROL_HEIGHT
	var popup := menu.get_popup()
	popup.add_item("Display & Interface Settings", 0)
	popup.add_item("Fit Window to Screen", 1)
	popup.add_separator()
	popup.add_item("Reset UI Scale", 2)
	popup.id_pressed.connect(_on_menu_action)
	toolbar.add_child(menu)

	var settings_button := Button.new()
	settings_button.text = "Settings"
	settings_button.custom_minimum_size.y = CONTROL_HEIGHT
	settings_button.pressed.connect(_open_settings)
	toolbar.add_child(settings_button)

	var spacer := Control.new()
	spacer.custom_minimum_size = Vector2(8, 1)
	spacer.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	toolbar.add_child(spacer)

	_display_label = Label.new()
	_display_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT
	_display_label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	_display_label.modulate = Color("aeb8c4")
	toolbar.add_child(_display_label)

	root_box.add_child(toolbar)
	root_box.move_child(toolbar, mini(1, root_box.get_child_count() - 1))

func _on_menu_action(id: int) -> void:
	match id:
		0:
			_open_settings()
		1:
			if _settings != null:
				_settings.fit_window_to_screen()
		2:
			if _settings != null:
				_settings.reset_ui_scale()

func _open_settings() -> void:
	if _settings != null:
		_settings.open()

func _on_settings_applied() -> void:
	_normalize_subtree(_root_control)
	_on_viewport_changed()

func _on_viewport_changed() -> void:
	_update_popup_constraints(_root_control)
	_update_display_label()

func _update_display_label() -> void:
	if _display_label == null:
		return
	var window := get_tree().root
	_display_label.text = "%d×%d • UI %d%%" % [
		window.size.x,
		window.size.y,
		int(round(window.content_scale_factor * 100.0)),
	]

func _on_node_added(node: Node) -> void:
	if _root_control == null or node == _root_control or not _root_control.is_ancestor_of(node):
		return
	var id := node.get_instance_id()
	if _normalization_pending.has(id):
		return
	_normalization_pending[id] = true
	call_deferred("_normalize_dynamic_node", node, id)

func _normalize_dynamic_node(node: Node, id: int) -> void:
	_normalization_pending.erase(id)
	if not is_instance_valid(node) or _root_control == null or not _root_control.is_ancestor_of(node):
		return
	if node is HBoxContainer and _should_wrap_dynamic_hbox(node as HBoxContainer):
		node = _replace_hbox_with_flow(node as HBoxContainer)
	if is_instance_valid(node):
		_normalize_subtree(node)

func _should_wrap_dynamic_hbox(row: HBoxContainer) -> bool:
	if row.name.to_lower().contains("responsive"):
		return false
	var parent := row.get_parent()
	return parent is VBoxContainer or parent is PanelContainer or parent is ScrollContainer

func _replace_hbox_with_flow(row: HBoxContainer) -> Control:
	var parent := row.get_parent()
	if parent == null:
		return row
	var replacement := HFlowContainer.new()
	replacement.name = "%sResponsive" % row.name
	replacement.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	replacement.size_flags_vertical = row.size_flags_vertical
	replacement.add_theme_constant_override("h_separation", 8)
	replacement.add_theme_constant_override("v_separation", 6)
	var old_index := row.get_index()
	parent.add_child(replacement)
	parent.move_child(replacement, old_index)
	for child in row.get_children():
		child.reparent(replacement)
	row.queue_free()
	return replacement

func _normalize_subtree(parent: Node) -> void:
	if parent is Control:
		_normalize_control(parent as Control)
	for child in parent.get_children():
		_normalize_subtree(child)

func _normalize_control(control: Control) -> void:
	control.custom_minimum_size.x = 0.0

	if control is PanelContainer:
		_style_panel(control as PanelContainer)
	if control is Button:
		var button := control as Button
		button.clip_text = true
		button.text_overrun_behavior = TextServer.OVERRUN_TRIM_ELLIPSIS
		button.custom_minimum_size.y = maxf(button.custom_minimum_size.y, CONTROL_HEIGHT)
	if control is LineEdit:
		control.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		control.custom_minimum_size.y = maxf(control.custom_minimum_size.y, CONTROL_HEIGHT)
	if control is SpinBox:
		control.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		control.custom_minimum_size.y = maxf(control.custom_minimum_size.y, CONTROL_HEIGHT)
	if control is OptionButton:
		_configure_option_button(control as OptionButton)
	if control is Label:
		var label := control as Label
		if label.autowrap_mode == TextServer.AUTOWRAP_OFF:
			label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	if control is RichTextLabel:
		control.custom_minimum_size = Vector2(0, 120)
	if control is ScrollContainer:
		var scroll := control as ScrollContainer
		scroll.vertical_scroll_mode = ScrollContainer.SCROLL_MODE_AUTO

func _style_panel(panel: PanelContainer) -> void:
	if panel.has_theme_stylebox_override("panel"):
		return
	var style := StyleBoxFlat.new()
	style.bg_color = PANEL_BG
	style.border_color = PANEL_BORDER
	style.set_border_width_all(1)
	style.set_corner_radius_all(8)
	style.content_margin_left = 10
	style.content_margin_right = 10
	style.content_margin_top = 9
	style.content_margin_bottom = 9
	panel.add_theme_stylebox_override("panel", style)

func _configure_option_button(option: OptionButton) -> void:
	option.fit_to_longest_item = false
	option.clip_text = true
	option.text_overrun_behavior = TextServer.OVERRUN_TRIM_ELLIPSIS
	option.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	option.custom_minimum_size = Vector2(0, maxf(option.custom_minimum_size.y, CONTROL_HEIGHT))
	var popup := option.get_popup()
	popup.prefer_native_menu = false
	popup.search_bar_enabled = true
	popup.search_bar_min_item_count = 8
	popup.shrink_width = true
	if not option.has_meta(CONFIGURED_META):
		option.item_selected.connect(_sync_option_tooltip.bind(option))
		option.set_meta(CONFIGURED_META, true)
	_sync_option_tooltip(option.selected, option)
	_constrain_popup(popup)

func _sync_option_tooltip(index: int, option: OptionButton) -> void:
	if index >= 0 and index < option.item_count:
		option.tooltip_text = option.get_item_text(index)
	else:
		option.tooltip_text = ""

func _update_popup_constraints(parent: Node) -> void:
	if parent is OptionButton:
		_constrain_popup((parent as OptionButton).get_popup())
	elif parent is MenuButton:
		_constrain_popup((parent as MenuButton).get_popup())
	for child in parent.get_children():
		_update_popup_constraints(child)

func _constrain_popup(popup: PopupMenu) -> void:
	var visible_size := get_viewport().get_visible_rect().size
	var max_width := maxi(240, int(visible_size.x) - 32)
	var max_height := maxi(180, int(visible_size.y) - 48)
	popup.max_size = Vector2i(mini(560, max_width), mini(440, max_height))

func _find_primary_vbox(parent: Node) -> VBoxContainer:
	for child in parent.get_children():
		if child is VBoxContainer:
			return child as VBoxContainer
		var nested := _find_primary_vbox(child)
		if nested != null:
			return nested
	return null
