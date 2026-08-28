class_name CivilizationResponsiveLayout
extends Node

const NARROW_WIDTH := 960.0
const COMPACT_WIDTH := 700.0
const TINY_WIDTH := 520.0
const MAP_MIN_WIDE := Vector2(320.0, 280.0)
const MAP_MIN_NARROW := Vector2(220.0, 200.0)
const SECTION_TITLES := [
	"Research",
	"Settlement / Production",
	"Diplomacy",
	"Turn",
	"Authorized Events",
]

var _installed := false
var _split: SplitContainer
var _grids: Array[GridContainer] = []
var _map: CivilizationHexMap
var _lobby_scroll: ScrollContainer

func _ready() -> void:
	call_deferred("_install")

func _exit_tree() -> void:
	if get_viewport() != null and get_viewport().size_changed.is_connected(_apply_layout):
		get_viewport().size_changed.disconnect(_apply_layout)

func _install() -> void:
	if _installed:
		return
	var root := get_parent() as Control
	if root == null:
		return
	_replace_horizontal_rows(root)
	_replace_game_split(root)
	_wrap_lobby_panel(root)
	_group_sidebar_sections(root)
	_collect_and_relax_controls(root)
	get_viewport().size_changed.connect(_apply_layout)
	_installed = true
	_apply_layout()

func _replace_horizontal_rows(parent: Node) -> void:
	for child in parent.get_children():
		if child is HSplitContainer:
			_replace_horizontal_rows(child)
			continue
		if child is HBoxContainer:
			var old := child as HBoxContainer
			var flow := HFlowContainer.new()
			flow.name = "%sResponsive" % old.name
			flow.size_flags_horizontal = Control.SIZE_EXPAND_FILL
			flow.size_flags_vertical = old.size_flags_vertical
			flow.add_theme_constant_override("h_separation", 8)
			flow.add_theme_constant_override("v_separation", 6)
			var container_parent := old.get_parent()
			var old_index := old.get_index()
			container_parent.add_child(flow)
			container_parent.move_child(flow, old_index)
			for grandchild in old.get_children():
				grandchild.reparent(flow)
			old.queue_free()
			_replace_horizontal_rows(flow)
		else:
			_replace_horizontal_rows(child)

func _replace_game_split(root: Node) -> void:
	var old_split := _find_hsplit(root)
	if old_split == null:
		return
	var replacement := SplitContainer.new()
	replacement.name = "ResponsiveGameSplit"
	replacement.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	replacement.size_flags_vertical = Control.SIZE_EXPAND_FILL
	replacement.dragger_visibility = SplitContainer.DRAGGER_VISIBLE
	var split_parent := old_split.get_parent()
	var old_index := old_split.get_index()
	split_parent.add_child(replacement)
	split_parent.move_child(replacement, old_index)
	for child in old_split.get_children():
		child.reparent(replacement)
		if child is Control:
			var control := child as Control
			control.size_flags_horizontal = Control.SIZE_EXPAND_FILL
			control.size_flags_vertical = Control.SIZE_EXPAND_FILL
	old_split.queue_free()
	_split = replacement
	_apply_split_ratios(false)

func _wrap_lobby_panel(root: Node) -> void:
	var panel := _find_lobby_panel(root)
	if panel == null:
		return
	var panel_parent := panel.get_parent()
	var panel_index := panel.get_index()
	var scroll := ScrollContainer.new()
	scroll.name = "ResponsiveLobbyScroll"
	scroll.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	scroll.size_flags_vertical = Control.SIZE_EXPAND_FILL
	scroll.horizontal_scroll_mode = ScrollContainer.SCROLL_MODE_DISABLED
	scroll.vertical_scroll_mode = ScrollContainer.SCROLL_MODE_AUTO
	scroll.visible = panel.visible
	panel_parent.add_child(scroll)
	panel_parent.move_child(scroll, panel_index)
	panel.reparent(scroll)
	panel.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	panel.visibility_changed.connect(func() -> void: scroll.visible = panel.visible)
	_lobby_scroll = scroll

func _group_sidebar_sections(root: Node) -> void:
	var sidebar := _find_sidebar(root)
	if sidebar == null or bool(sidebar.get_meta("sections_grouped", false)):
		return
	sidebar.set_meta("sections_grouped", true)
	var groups: Array[Array] = []
	var current: Array = []
	for child in sidebar.get_children():
		if child is Label and SECTION_TITLES.has((child as Label).text):
			if not current.is_empty():
				groups.append(current)
			current = [child]
		elif not current.is_empty():
			current.append(child)
	if not current.is_empty():
		groups.append(current)
	for group in groups:
		if group.is_empty():
			continue
		var first := group[0] as Node
		var insertion_index := first.get_index()
		var panel := PanelContainer.new()
		panel.name = "SidebarCard"
		panel.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		var body := VBoxContainer.new()
		body.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		body.add_theme_constant_override("separation", 8)
		sidebar.add_child(panel)
		sidebar.move_child(panel, insertion_index)
		panel.add_child(body)
		for grouped_node in group:
			(grouped_node as Node).reparent(body)

func _find_sidebar(parent: Node) -> VBoxContainer:
	for child in parent.get_children():
		if child is VBoxContainer:
			var candidate := child as VBoxContainer
			for direct_child in candidate.get_children():
				if direct_child is Label and SECTION_TITLES.has((direct_child as Label).text):
					return candidate
		var nested := _find_sidebar(child)
		if nested != null:
			return nested
	return null

func _find_hsplit(parent: Node) -> HSplitContainer:
	for child in parent.get_children():
		if child is HSplitContainer:
			return child as HSplitContainer
		var nested := _find_hsplit(child)
		if nested != null:
			return nested
	return null

func _find_lobby_panel(parent: Node) -> PanelContainer:
	for child in parent.get_children():
		if child is PanelContainer and _contains_nonbutton_grid(child):
			return child as PanelContainer
		var nested := _find_lobby_panel(child)
		if nested != null:
			return nested
	return null

func _contains_nonbutton_grid(parent: Node) -> bool:
	for child in parent.get_children():
		if child is GridContainer:
			for grid_child in child.get_children():
				if not grid_child is Button:
					return true
		if _contains_nonbutton_grid(child):
			return true
	return false

func _collect_and_relax_controls(parent: Node) -> void:
	_grids.clear()
	_map = null
	_collect_controls(parent)

func _collect_controls(parent: Node) -> void:
	for child in parent.get_children():
		if child is Control:
			var control := child as Control
			control.custom_minimum_size.x = 0.0
			if control is LineEdit or control is OptionButton or control is SpinBox:
				control.size_flags_horizontal = Control.SIZE_EXPAND_FILL
			if control is Button:
				var button := control as Button
				button.clip_text = true
				button.text_overrun_behavior = TextServer.OVERRUN_TRIM_ELLIPSIS
			if control is OptionButton:
				(control as OptionButton).fit_to_longest_item = false
			if control is Label:
				(control as Label).autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
			if control is RichTextLabel:
				control.custom_minimum_size = Vector2(0.0, 140.0)
			if control is ScrollContainer:
				var scroll := control as ScrollContainer
				scroll.horizontal_scroll_mode = ScrollContainer.SCROLL_MODE_DISABLED
				scroll.vertical_scroll_mode = ScrollContainer.SCROLL_MODE_AUTO
			if control is GridContainer:
				_grids.append(control as GridContainer)
			if control is CivilizationHexMap:
				_map = control as CivilizationHexMap
		_collect_controls(child)

func _apply_layout() -> void:
	if not _installed:
		return
	var width := get_viewport().get_visible_rect().size.x
	var narrow := width < NARROW_WIDTH
	var compact := width < COMPACT_WIDTH
	var tiny := width < TINY_WIDTH
	if _split != null:
		_split.vertical = narrow
		_split.split_offset = 0
		_apply_split_ratios(narrow)
	if _map != null:
		_map.custom_minimum_size = MAP_MIN_NARROW if narrow else MAP_MIN_WIDE
	for grid in _grids:
		var only_buttons := true
		for child in grid.get_children():
			if not child is Button:
				only_buttons = false
				break
		if only_buttons:
			grid.columns = 1 if compact else 2
		else:
			grid.columns = 1 if tiny else (2 if narrow else 4)

func _apply_split_ratios(narrow: bool) -> void:
	if _split == null or _split.get_child_count() < 2:
		return
	var primary := _split.get_child(0) as Control
	var secondary := _split.get_child(1) as Control
	if primary == null or secondary == null:
		return
	primary.size_flags_stretch_ratio = 1.25 if narrow else 2.0
	secondary.size_flags_stretch_ratio = 1.0
