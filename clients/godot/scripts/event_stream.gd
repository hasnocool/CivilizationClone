class_name CivilizationEventStream
extends Node

signal event_received(event: Dictionary)
signal status_changed(status: String)
signal stream_error(message: String)

const MAX_RETRY_SECONDS := 8.0

var _peer: WebSocketPeer
var _url: String = ""
var _protocols := PackedStringArray()
var _active := false
var _retry_attempt := 0
var _retry_at_msec := 0
var _last_state := -1

func _ready() -> void:
	set_process(false)

func connect_stream(url: String, protocols: PackedStringArray) -> void:
	disconnect_stream(false)
	_url = url
	_protocols = protocols
	_active = true
	_retry_attempt = 0
	_retry_at_msec = 0
	set_process(true)
	_open_peer()

func disconnect_stream(emit_status: bool = true) -> void:
	_active = false
	_retry_at_msec = 0
	_retry_attempt = 0
	if _peer != null:
		var state := _peer.get_ready_state()
		if state == WebSocketPeer.STATE_OPEN or state == WebSocketPeer.STATE_CONNECTING:
			_peer.close(1000, "client session changed")
	_peer = null
	_last_state = -1
	set_process(false)
	if emit_status:
		status_changed.emit("offline")

func _exit_tree() -> void:
	disconnect_stream(false)

func _process(_delta: float) -> void:
	if not _active:
		return
	if _peer == null:
		if _retry_at_msec <= 0 or Time.get_ticks_msec() >= _retry_at_msec:
			_open_peer()
		return

	_peer.poll()
	var state := _peer.get_ready_state()
	if state != _last_state:
		_last_state = state
		match state:
			WebSocketPeer.STATE_CONNECTING:
				status_changed.emit("connecting")
			WebSocketPeer.STATE_OPEN:
				_retry_attempt = 0
				_retry_at_msec = 0
				status_changed.emit("live")
			WebSocketPeer.STATE_CLOSING:
				status_changed.emit("closing")
			WebSocketPeer.STATE_CLOSED:
				_handle_closed_peer()
				return

	if state == WebSocketPeer.STATE_OPEN:
		while _peer.get_available_packet_count() > 0:
			var packet := _peer.get_packet()
			if not _peer.was_string_packet():
				stream_error.emit("ignored non-text WebSocket event packet")
				continue
			var parsed := JSON.parse_string(packet.get_string_from_utf8())
			if parsed is Dictionary:
				event_received.emit(parsed)
			else:
				stream_error.emit("ignored invalid WebSocket event JSON")

func _open_peer() -> void:
	if not _active or _url.is_empty() or _protocols.size() != 2:
		return
	var peer := WebSocketPeer.new()
	peer.supported_protocols = _protocols
	peer.heartbeat_interval = 20.0
	var error := peer.connect_to_url(_url)
	if error != OK:
		stream_error.emit("live event connection could not start (%s)" % error_string(error))
		_peer = null
		_schedule_retry()
		return
	_peer = peer
	_last_state = WebSocketPeer.STATE_CONNECTING
	status_changed.emit("connecting")

func _handle_closed_peer() -> void:
	if _peer == null:
		return
	var code := _peer.get_close_code()
	var reason := _peer.get_close_reason()
	_peer = null
	_last_state = -1
	if not _active:
		return
	if code == 1008:
		_active = false
		set_process(false)
		status_changed.emit("unauthorized")
		stream_error.emit("live event credential was rejected")
		return
	if not reason.is_empty():
		stream_error.emit("live event stream closed (%d): %s" % [code, reason])
	_schedule_retry()

func _schedule_retry() -> void:
	if not _active:
		return
	_retry_attempt += 1
	var delay_seconds := minf(MAX_RETRY_SECONDS, pow(2.0, float(_retry_attempt - 1)))
	_retry_at_msec = Time.get_ticks_msec() + int(delay_seconds * 1000.0)
	status_changed.emit("reconnecting in %.0fs" % delay_seconds)
