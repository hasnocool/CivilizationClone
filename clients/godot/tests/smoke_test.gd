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
	if _contains_hsplit(main):
		_fail("Fixed horizontal split remained after responsive installation")
		return
	if _contains_hbox(main):
		_fail("Fixed horizontal row remained after responsive installation")
		return
	var map := _find_map(main)
	if map == null:
		_fail("Hex map was not created")
		return
	if map.custom_minimum_size.x > 320.0 or map.custom_minimum_size.y > 280.0:
		_fail("Hex map retains an oversized fixed minimum")
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
