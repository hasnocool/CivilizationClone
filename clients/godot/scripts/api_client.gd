class_name CivilizationApiClient
extends Node

var base_url: String = "http://127.0.0.1:8000"
var timeout_seconds: float = 10.0
var _command_number: int = 0
var _client_id: String

func _ready() -> void:
	_client_id = "%x-%x" % [Time.get_ticks_usec(), randi()]

func configure(url: String) -> void:
	base_url = url.strip_edges().trim_suffix("/")

func health() -> Dictionary:
	return await _request_json(HTTPClient.METHOD_GET, "/api/v1/health")

func civilizations() -> Dictionary:
	return await _request_json(HTTPClient.METHOD_GET, "/api/v1/rules/civilizations")

func create_game(
	game_id: String,
	seed: int,
	player_count: int,
	map_radius: int = 4,
	water_percent: int = 20,
	resource_percent: int = 18
) -> Dictionary:
	return await _request_json(
		HTTPClient.METHOD_POST,
		"/api/v1/games",
		{
			"game_id": game_id,
			"seed": seed,
			"player_count": player_count,
			"map_radius": map_radius,
			"water_percent": water_percent,
			"resource_percent": resource_percent,
		}
	)

func join_player(
	game_id: String,
	admin_token: String,
	player_id: String,
	player_name: String,
	civilization_id: String,
	controller: String = "human"
) -> Dictionary:
	return await _request_json(
		HTTPClient.METHOD_POST,
		"/api/v1/games/%s/players" % game_id.uri_encode(),
		{
			"command_id": _next_command_id("join"),
			"player_id": player_id,
			"name": player_name,
			"controller": controller,
			"civilization_id": civilization_id,
		},
		admin_token
	)

func start_game(game_id: String, admin_token: String) -> Dictionary:
	return await command(game_id, admin_token, "StartGame", "", -1, {})

func command(
	game_id: String,
	token: String,
	command_type: String,
	player_id: String,
	expected_state_version: int,
	payload: Dictionary
) -> Dictionary:
	var body: Dictionary = {
		"command_id": _next_command_id(command_type.to_lower()),
		"command_type": command_type,
		"payload": payload,
		"client_timestamp": Time.get_datetime_string_from_system(true, false),
	}
	if not player_id.is_empty():
		body["player_id"] = player_id
	if expected_state_version >= 0:
		body["expected_state_version"] = expected_state_version
	return await _request_json(
		HTTPClient.METHOD_POST,
		"/api/v1/games/%s/commands" % game_id.uri_encode(),
		body,
		token
	)

func state(game_id: String, player_token: String) -> Dictionary:
	return await _request_json(
		HTTPClient.METHOD_GET,
		"/api/v1/games/%s/state" % game_id.uri_encode(),
		null,
		player_token
	)

func legal_actions(game_id: String, player_token: String) -> Dictionary:
	return await _request_json(
		HTTPClient.METHOD_GET,
		"/api/v1/games/%s/legal-actions" % game_id.uri_encode(),
		null,
		player_token
	)

func events(game_id: String, player_token: String, after_sequence: int = -1) -> Dictionary:
	return await _request_json(
		HTTPClient.METHOD_GET,
		"/api/v1/games/%s/events?after_sequence=%d" % [game_id.uri_encode(), after_sequence],
		null,
		player_token
	)

func event_websocket_url(game_id: String, after_sequence: int = -1) -> String:
	var websocket_base := base_url
	if websocket_base.begins_with("https://"):
		websocket_base = "wss://" + websocket_base.substr(8)
	elif websocket_base.begins_with("http://"):
		websocket_base = "ws://" + websocket_base.substr(7)
	return "%s/api/v1/games/%s/events/ws?after_sequence=%d" % [
		websocket_base,
		game_id.uri_encode(),
		after_sequence,
	]

func event_websocket_protocols(player_token: String) -> PackedStringArray:
	return PackedStringArray(["civilization.v1", player_token])

func _next_command_id(prefix: String) -> String:
	_command_number += 1
	return "godot-%s-%s-%d" % [_client_id, prefix, _command_number]

func _request_json(
	method: HTTPClient.Method,
	path: String,
	payload: Variant = null,
	token: String = ""
) -> Dictionary:
	var request := HTTPRequest.new()
	request.timeout = timeout_seconds
	add_child(request)

	var headers := PackedStringArray(["Accept: application/json"])
	var body := ""
	if payload != null:
		headers.append("Content-Type: application/json")
		body = JSON.stringify(payload)
	if not token.is_empty():
		headers.append("Authorization: Bearer %s" % token)

	var error := request.request(base_url + path, headers, method, body)
	if error != OK:
		request.queue_free()
		return {
			"ok": false,
			"status": 0,
			"detail": "request could not be started (%s)" % error_string(error),
			"data": null,
		}

	var completed: Array = await request.request_completed
	var transport_result := int(completed[0])
	var response_code := int(completed[1])
	var response_body: PackedByteArray = completed[3]
	request.queue_free()

	if transport_result != HTTPRequest.RESULT_SUCCESS:
		return {
			"ok": false,
			"status": 0,
			"detail": "network request failed (%d)" % transport_result,
			"data": null,
		}

	var raw := response_body.get_string_from_utf8()
	var parsed: Variant = null
	if not raw.is_empty():
		parsed = JSON.parse_string(raw)
		if parsed == null and raw.strip_edges() != "null":
			return {
				"ok": false,
				"status": response_code,
				"detail": "server returned invalid JSON",
				"data": null,
			}

	if response_code < 200 or response_code >= 300:
		var detail := "HTTP %d" % response_code
		if parsed is Dictionary and parsed.has("detail"):
			detail = str(parsed["detail"])
		return {
			"ok": false,
			"status": response_code,
			"detail": detail,
			"data": parsed,
		}

	return {
		"ok": true,
		"status": response_code,
		"detail": "",
		"data": parsed,
	}
