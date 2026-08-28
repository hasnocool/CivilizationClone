class_name CivilizationHexMap
extends Control

signal tile_clicked(q: int, r: int)

@export var preferred_hex_size: float = 30.0
@export var maximum_hex_size: float = 48.0
@export var minimum_hex_size: float = 4.0

var game_state: Dictionary = {}
var selected_unit_id: String = ""
var selected_tile := Vector2i(999999, 999999)
var _centers: Dictionary = {}
var _draw_hex_size: float = 30.0
var _draw_origin := Vector2.ZERO

func _ready() -> void:
	mouse_filter = Control.MOUSE_FILTER_STOP
	resized.connect(queue_redraw)

func set_state(value: Dictionary) -> void:
	game_state = value
	queue_redraw()

func set_selected_unit(unit_id: String) -> void:
	selected_unit_id = unit_id
	queue_redraw()

func set_selected_tile(q: int, r: int) -> void:
	selected_tile = Vector2i(q, r)
	queue_redraw()

func _draw() -> void:
	draw_rect(Rect2(Vector2.ZERO, size), Color("10151d"), true)
	_centers.clear()
	if game_state.is_empty():
		_draw_center_text("Connect to an API and start a game")
		return

	var map_data: Dictionary = game_state.get("map", {})
	var tiles: Array = map_data.get("tiles", [])
	if tiles.is_empty():
		_draw_center_text("No authorized map tiles")
		return

	_fit_map_to_control(tiles)
	for raw_tile in tiles:
		if not raw_tile is Dictionary:
			continue
		var q := int(raw_tile.get("q", 0))
		var r := int(raw_tile.get("r", 0))
		var center := _draw_origin + _axial_to_pixel(q, r, _draw_hex_size)
		_centers[Vector2i(q, r)] = center
		var color := _terrain_color(str(raw_tile.get("terrain", "unknown")))
		if str(raw_tile.get("visibility", "visible")) == "discovered":
			color = color.darkened(0.42)
		var polygon := _hex_points(center, _draw_hex_size)
		draw_colored_polygon(polygon, color)
		draw_polyline(PackedVector2Array(Array(polygon) + [polygon[0]]), Color("556274"), 1.0, true)
		if raw_tile.get("resource") != null:
			draw_circle(
				center + Vector2(_draw_hex_size * 0.45, -_draw_hex_size * 0.35),
				maxf(2.0, _draw_hex_size * 0.11),
				Color("f6d365")
			)
		if selected_tile == Vector2i(q, r):
			draw_polyline(PackedVector2Array(Array(polygon) + [polygon[0]]), Color("ffffff"), 3.0, true)

	_draw_settlements()
	_draw_units()

func _fit_map_to_control(tiles: Array) -> void:
	var min_x := INF
	var max_x := -INF
	var min_y := INF
	var max_y := -INF
	for raw_tile in tiles:
		if not raw_tile is Dictionary:
			continue
		var unit_position := _axial_to_pixel(int(raw_tile.get("q", 0)), int(raw_tile.get("r", 0)), 1.0)
		min_x = minf(min_x, unit_position.x)
		max_x = maxf(max_x, unit_position.x)
		min_y = minf(min_y, unit_position.y)
		max_y = maxf(max_y, unit_position.y)
	if min_x == INF:
		_draw_hex_size = preferred_hex_size
		_draw_origin = size * 0.5
		return

	var available := Vector2(maxf(1.0, size.x - 24.0), maxf(1.0, size.y - 24.0))
	var unit_width := maxf(1.0, max_x - min_x + sqrt(3.0))
	var unit_height := maxf(1.0, max_y - min_y + 2.0)
	var fitted := minf(available.x / unit_width, available.y / unit_height)
	_draw_hex_size = clampf(fitted, minimum_hex_size, maximum_hex_size)
	var unit_center := Vector2((min_x + max_x) * 0.5, (min_y + max_y) * 0.5)
	_draw_origin = size * 0.5 - unit_center * _draw_hex_size

func _draw_settlements() -> void:
	var viewer_id := str(game_state.get("viewer", {}).get("player_id", ""))
	for raw in game_state.get("settlements", []):
		if not raw is Dictionary:
			continue
		var center := _draw_origin + _axial_to_pixel(
			int(raw.get("q", 0)), int(raw.get("r", 0)), _draw_hex_size
		)
		var own := str(raw.get("owner_id", "")) == viewer_id
		var color := Color("7ee081") if own else Color("f28b82")
		draw_circle(center, _draw_hex_size * 0.35, Color(color, 0.88))
		if _draw_hex_size >= 10.0:
			draw_string(
				ThemeDB.fallback_font,
				center + Vector2(-7, 6),
				"S",
				HORIZONTAL_ALIGNMENT_LEFT,
				-1,
				clampi(int(_draw_hex_size * 0.55), 10, 18),
				Color("10151d")
			)

func _draw_units() -> void:
	var viewer_id := str(game_state.get("viewer", {}).get("player_id", ""))
	for raw in game_state.get("units", []):
		if not raw is Dictionary:
			continue
		var center := _draw_origin + _axial_to_pixel(
			int(raw.get("q", 0)), int(raw.get("r", 0)), _draw_hex_size
		)
		var own := str(raw.get("owner_id", "")) == viewer_id
		var color := Color("80cbc4") if own else Color("ff8a80")
		var radius := _draw_hex_size * 0.22
		draw_circle(center, radius, color)
		if str(raw.get("unit_id", "")) == selected_unit_id:
			draw_arc(center, radius + maxf(2.0, _draw_hex_size * 0.16), 0.0, TAU, 32, Color.WHITE, 3.0, true)
		if _draw_hex_size >= 10.0:
			draw_string(
				ThemeDB.fallback_font,
				center + Vector2(-5, 5),
				"U",
				HORIZONTAL_ALIGNMENT_LEFT,
				-1,
				clampi(int(_draw_hex_size * 0.45), 9, 15),
				Color("10151d")
			)

func _gui_input(event: InputEvent) -> void:
	if event is InputEventMouseButton and event.button_index == MOUSE_BUTTON_LEFT and event.pressed:
		var best_coord := Vector2i(999999, 999999)
		var best_distance := INF
		for coord: Vector2i in _centers:
			var center: Vector2 = _centers[coord]
			var current_distance := center.distance_to(event.position)
			if current_distance < best_distance:
				best_distance = current_distance
				best_coord = coord
		if best_distance <= maxf(_draw_hex_size, 8.0):
			set_selected_tile(best_coord.x, best_coord.y)
			tile_clicked.emit(best_coord.x, best_coord.y)

func _axial_to_pixel(q: int, r: int, hex_radius: float) -> Vector2:
	return Vector2(
		hex_radius * sqrt(3.0) * (float(q) + float(r) * 0.5),
		hex_radius * 1.5 * float(r)
	)

func _hex_points(center: Vector2, hex_radius: float) -> PackedVector2Array:
	var points := PackedVector2Array()
	for index in range(6):
		var angle := deg_to_rad(60.0 * float(index) - 30.0)
		points.append(center + Vector2(cos(angle), sin(angle)) * hex_radius)
	return points

func _terrain_color(terrain: String) -> Color:
	match terrain:
		"water":
			return Color("355c7d")
		"plains":
			return Color("b7a66a")
		"grassland":
			return Color("6d9f71")
		"hills":
			return Color("8d795f")
		"desert":
			return Color("c9a66b")
		"tundra":
			return Color("9aa6a9")
		_:
			return Color("495057")

func _draw_center_text(text: String) -> void:
	var font_size := clampi(int(size.x / 35.0), 12, 18)
	var text_size := ThemeDB.fallback_font.get_string_size(text, HORIZONTAL_ALIGNMENT_LEFT, -1, font_size)
	draw_string(
		ThemeDB.fallback_font,
		size * 0.5 - text_size * 0.5,
		text,
		HORIZONTAL_ALIGNMENT_LEFT,
		-1,
		font_size,
		Color("aeb8c4")
	)
