class_name CivilizationSettingsScreen
extends Control

signal settings_applied

const SETTINGS_PATH := "user://client_settings.cfg"
const MIN_WINDOW_SIZE := Vector2i(640, 480)
const DEFAULT_WINDOW_SIZE := Vector2i(1280, 720)
const FIT_SCREEN_SENTINEL := Vector2i(-1, -1)
const RESOLUTIONS := [
	Vector2i(800, 600),
	Vector2i(1024, 576),
	Vector2i(1024, 768),
	Vector2i(1280, 720),
	Vector2i(1366, 768),
	Vector2i(1600, 900),
	Vector2i(1920, 1080),
	Vector2i(2560, 1440),
]
const UI_SCALES := [0.75, 0.85, 1.0, 1.1, 1.25, 1.5, 1.75]

var mode_select: OptionButton
var resolution_select: OptionButton
var ui_scale_select: OptionButton
var current_display_label: Label
var feedback_label: Label
var settings_scroll: ScrollContainer
var _config := ConfigFile.new()
var _saved_window_size := DEFAULT_WINDOW_SIZE

func _ready() -> void:
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	mouse_filter = Control.MOUSE_FILTER_STOP
	z_index = 1000
	_build_screen()
	_load_settings()
	_apply_saved_settings()
	visible = false
	get_viewport().size_changed.connect(_refresh_current_display)

func open() -> void:
	_sync_controls_from_runtime()
	_refresh_current_display()
	visible = true
	grab_focus()

func close() -> void:
	visible = false

func fit_window_to_screen() -> void:
	_select_option_by_metadata(mode_select, Window.MODE_WINDOWED)
	_select_option_by_metadata(resolution_select, FIT_SCREEN_SENTINEL)
	_apply_controls()

func reset_ui_scale() -> void:
	_select_option_by_metadata(ui_scale_select, 1.0)
	_apply_controls()

func _unhandled_key_input(event: InputEvent) -> void:
	if visible and event.is_action_pressed("ui_cancel"):
		close()
		get_viewport().set_input_as_handled()

func _build_screen() -> void:
	var shade := ColorRect.new()
	shade.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	shade.color = Color(0.025, 0.03, 0.04, 0.92)
	shade.mouse_filter = Control.MOUSE_FILTER_STOP
	add_child(shade)

	var margin := MarginContainer.new()
	margin.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	margin.add_theme_constant_override("margin_left", 16)
	margin.add_theme_constant_override("margin_right", 16)
	margin.add_theme_constant_override("margin_top", 16)
	margin.add_theme_constant_override("margin_bottom", 16)
	add_child(margin)

	var panel := PanelContainer.new()
	panel.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	panel.size_flags_vertical = Control.SIZE_EXPAND_FILL
	panel.add_theme_stylebox_override("panel", _panel_style())
	margin.add_child(panel)

	var shell := VBoxContainer.new()
	shell.add_theme_constant_override("separation", 12)
	panel.add_child(shell)

	var header := HFlowContainer.new()
	header.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	header.add_theme_constant_override("h_separation", 10)
	header.add_theme_constant_override("v_separation", 8)
	shell.add_child(header)

	var title := Label.new()
	title.text = "Display & Interface Settings"
	title.add_theme_font_size_override("font_size", 22)
	title.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	header.add_child(title)

	var close_button := _button("Close")
	close_button.pressed.connect(close)
	header.add_child(close_button)

	current_display_label = Label.new()
	current_display_label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	current_display_label.modulate = Color("aeb8c4")
	shell.add_child(current_display_label)

	settings_scroll = ScrollContainer.new()
	settings_scroll.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	settings_scroll.size_flags_vertical = Control.SIZE_EXPAND_FILL
	settings_scroll.horizontal_scroll_mode = ScrollContainer.SCROLL_MODE_DISABLED
	settings_scroll.vertical_scroll_mode = ScrollContainer.SCROLL_MODE_AUTO
	shell.add_child(settings_scroll)

	var content := VBoxContainer.new()
	content.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	content.add_theme_constant_override("separation", 14)
	settings_scroll.add_child(content)

	content.add_child(_section_label("Window"))
	content.add_child(_help_text("Choose how the client uses the display. Windowed mode uses the selected resolution; maximized and fullscreen modes use the current screen."))

	mode_select = _dropdown()
	mode_select.add_item("Windowed")
	mode_select.set_item_metadata(0, Window.MODE_WINDOWED)
	mode_select.add_item("Maximized")
	mode_select.set_item_metadata(1, Window.MODE_MAXIMIZED)
	mode_select.add_item("Fullscreen")
	mode_select.set_item_metadata(2, Window.MODE_FULLSCREEN)
	mode_select.add_item("Exclusive Fullscreen")
	mode_select.set_item_metadata(3, Window.MODE_EXCLUSIVE_FULLSCREEN)
	content.add_child(_setting_row("Window mode", mode_select))

	resolution_select = _dropdown()
	resolution_select.add_item("Fit to screen (90%)")
	resolution_select.set_item_metadata(0, FIT_SCREEN_SENTINEL)
	for resolution in RESOLUTIONS:
		resolution_select.add_item("%d × %d" % [resolution.x, resolution.y])
		resolution_select.set_item_metadata(resolution_select.item_count - 1, resolution)
	content.add_child(_setting_row("Windowed resolution", resolution_select))

	content.add_child(_section_label("Interface"))
	content.add_child(_help_text("UI scale changes menus, panels, labels, and controls without changing authoritative game state. Smaller values show more information; larger values improve readability."))

	ui_scale_select = _dropdown()
	for scale in UI_SCALES:
		ui_scale_select.add_item("%d%%" % int(round(scale * 100.0)))
		ui_scale_select.set_item_metadata(ui_scale_select.item_count - 1, scale)
	content.add_child(_setting_row("UI scale", ui_scale_select))

	content.add_child(_section_label("Responsive layout"))
	content.add_child(_help_text("The game view automatically changes from side-by-side panels to a stacked layout on narrow windows. Menus wrap, dense panels scroll, and dropdown popups are clamped to the visible viewport."))

	feedback_label = Label.new()
	feedback_label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	feedback_label.modulate = Color("9fc5e8")
	content.add_child(feedback_label)

	var actions := HFlowContainer.new()
	actions.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	actions.add_theme_constant_override("h_separation", 8)
	actions.add_theme_constant_override("v_separation", 8)
	content.add_child(actions)

	var apply_button := _button("Apply & Save")
	apply_button.pressed.connect(_apply_controls)
	actions.add_child(apply_button)

	var fit_button := _button("Fit Window to Screen")
	fit_button.pressed.connect(fit_window_to_screen)
	actions.add_child(fit_button)

	var reset_button := _button("Reset Defaults")
	reset_button.pressed.connect(_reset_defaults)
	actions.add_child(reset_button)

func _setting_row(label_text: String, control: Control) -> Control:
	var row := VBoxContainer.new()
	row.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	row.add_theme_constant_override("separation", 5)
	var label := Label.new()
	label.text = label_text
	label.add_theme_font_size_override("font_size", 14)
	row.add_child(label)
	control.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	row.add_child(control)
	return row

func _dropdown() -> OptionButton:
	var option := OptionButton.new()
	option.fit_to_longest_item = false
	option.clip_text = true
	option.custom_minimum_size = Vector2(0, 38)
	option.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	var popup := option.get_popup()
	popup.search_bar_enabled = true
	popup.search_bar_min_item_count = 8
	popup.max_size = Vector2i(560, 440)
	return option

func _button(text: String) -> Button:
	var button := Button.new()
	button.text = text
	button.clip_text = true
	button.text_overrun_behavior = TextServer.OVERRUN_TRIM_ELLIPSIS
	button.custom_minimum_size.y = 38
	return button

func _section_label(text: String) -> Label:
	var label := Label.new()
	label.text = text
	label.add_theme_font_size_override("font_size", 18)
	return label

func _help_text(text: String) -> Label:
	var label := Label.new()
	label.text = text
	label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	label.modulate = Color("aeb8c4")
	return label

func _panel_style() -> StyleBoxFlat:
	var style := StyleBoxFlat.new()
	style.bg_color = Color("151b24")
	style.border_color = Color("334155")
	style.set_border_width_all(1)
	style.set_corner_radius_all(10)
	style.content_margin_left = 14
	style.content_margin_right = 14
	style.content_margin_top = 12
	style.content_margin_bottom = 12
	return style

func _load_settings() -> void:
	var error := _config.load(SETTINGS_PATH)
	if error != OK:
		_saved_window_size = DEFAULT_WINDOW_SIZE
		return
	_saved_window_size = Vector2i(
		int(_config.get_value("display", "window_width", DEFAULT_WINDOW_SIZE.x)),
		int(_config.get_value("display", "window_height", DEFAULT_WINDOW_SIZE.y))
	)

func _apply_saved_settings() -> void:
	var root_window := get_tree().root
	root_window.min_size = MIN_WINDOW_SIZE
	root_window.content_scale_mode = Window.CONTENT_SCALE_MODE_DISABLED
	root_window.content_scale_factor = clampf(float(_config.get_value("interface", "ui_scale", 1.0)), 0.75, 1.75)
	var saved_mode := int(_config.get_value("display", "window_mode", Window.MODE_WINDOWED))
	_apply_window(saved_mode, _saved_window_size, false)
	_sync_controls_from_runtime()

func _sync_controls_from_runtime() -> void:
	if mode_select == null:
		return
	var root_window := get_tree().root
	_select_option_by_metadata(mode_select, root_window.mode)
	var desired_resolution := _saved_window_size
	if not _select_option_by_metadata(resolution_select, desired_resolution):
		resolution_select.add_item("%d × %d (custom)" % [desired_resolution.x, desired_resolution.y])
		resolution_select.set_item_metadata(resolution_select.item_count - 1, desired_resolution)
		resolution_select.select(resolution_select.item_count - 1)
	_select_nearest_scale(root_window.content_scale_factor)

func _apply_controls() -> void:
	var mode := int(mode_select.get_item_metadata(mode_select.selected))
	var resolution: Vector2i = resolution_select.get_item_metadata(resolution_select.selected)
	var scale := float(ui_scale_select.get_item_metadata(ui_scale_select.selected))
	if resolution == FIT_SCREEN_SENTINEL:
		resolution = _fit_resolution()
	_saved_window_size = resolution
	var root_window := get_tree().root
	root_window.content_scale_factor = clampf(scale, 0.75, 1.75)
	_apply_window(mode, resolution, true)
	_config.set_value("display", "window_mode", mode)
	_config.set_value("display", "window_width", resolution.x)
	_config.set_value("display", "window_height", resolution.y)
	_config.set_value("interface", "ui_scale", root_window.content_scale_factor)
	var save_error := _config.save(SETTINGS_PATH)
	feedback_label.text = "Settings applied." if save_error == OK else "Settings applied, but preferences could not be saved."
	_refresh_current_display()
	settings_applied.emit()

func _apply_window(mode: int, requested_size: Vector2i, center_window: bool) -> void:
	var root_window := get_tree().root
	var safe_size := _clamp_windowed_size(requested_size)
	if mode == Window.MODE_WINDOWED:
		root_window.mode = Window.MODE_WINDOWED
		root_window.size = safe_size
		if center_window:
			_center_window(safe_size)
	elif mode == Window.MODE_MAXIMIZED:
		root_window.mode = Window.MODE_MAXIMIZED
	elif mode == Window.MODE_EXCLUSIVE_FULLSCREEN:
		root_window.mode = Window.MODE_EXCLUSIVE_FULLSCREEN
	else:
		root_window.mode = Window.MODE_FULLSCREEN

func _clamp_windowed_size(requested_size: Vector2i) -> Vector2i:
	var usable := DisplayServer.screen_get_usable_rect(get_tree().root.current_screen)
	var max_width := maxi(MIN_WINDOW_SIZE.x, usable.size.x - 24)
	var max_height := maxi(MIN_WINDOW_SIZE.y, usable.size.y - 24)
	return Vector2i(
		clampi(requested_size.x, MIN_WINDOW_SIZE.x, max_width),
		clampi(requested_size.y, MIN_WINDOW_SIZE.y, max_height)
	)

func _fit_resolution() -> Vector2i:
	var usable := DisplayServer.screen_get_usable_rect(get_tree().root.current_screen)
	return _clamp_windowed_size(Vector2i(
		int(round(float(usable.size.x) * 0.9)),
		int(round(float(usable.size.y) * 0.9))
	))

func _center_window(window_size: Vector2i) -> void:
	var root_window := get_tree().root
	var usable := DisplayServer.screen_get_usable_rect(root_window.current_screen)
	root_window.position = usable.position + (usable.size - window_size) / 2

func _reset_defaults() -> void:
	_select_option_by_metadata(mode_select, Window.MODE_WINDOWED)
	_select_option_by_metadata(resolution_select, DEFAULT_WINDOW_SIZE)
	_select_option_by_metadata(ui_scale_select, 1.0)
	_apply_controls()

func _select_nearest_scale(value: float) -> void:
	var best_index := 0
	var best_distance := INF
	for index in range(ui_scale_select.item_count):
		var candidate := float(ui_scale_select.get_item_metadata(index))
		var distance := absf(candidate - value)
		if distance < best_distance:
			best_distance = distance
			best_index = index
	ui_scale_select.select(best_index)

func _select_option_by_metadata(option: OptionButton, value: Variant) -> bool:
	for index in range(option.item_count):
		if option.get_item_metadata(index) == value:
			option.select(index)
			return true
	return false

func _refresh_current_display() -> void:
	if current_display_label == null:
		return
	var root_window := get_tree().root
	var mode_names := {
		Window.MODE_WINDOWED: "Windowed",
		Window.MODE_MAXIMIZED: "Maximized",
		Window.MODE_FULLSCREEN: "Fullscreen",
		Window.MODE_EXCLUSIVE_FULLSCREEN: "Exclusive Fullscreen",
	}
	current_display_label.text = "Current: %d × %d • %s • UI %d%%" % [
		root_window.size.x,
		root_window.size.y,
		mode_names.get(root_window.mode, "Window"),
		int(round(root_window.content_scale_factor * 100.0)),
	]
