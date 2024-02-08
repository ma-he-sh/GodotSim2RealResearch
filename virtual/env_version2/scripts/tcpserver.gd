extends Node

signal recieved_request(id, data)

var PORT=9000
var _server=WebSocketServer.new()

# background randomization : done
var randomize_background = false

# platform surface randomization : done
var randomize_platform_surface = false

# randomize lighting conditions | position : done
var randomize_lighting_intensity = false
var randomize_lighting_min_int = 0
var randomize_lighting_max_int = 16
# ----------------------------------------
var randomize_lighting_pos   = false
var randomize_lighting_pos_max_x = 78.0
var randomize_lighting_pos_min_x = -78.0
var randomize_lighting_pos_max_z = 78.0
var randomize_lighting_pos_min_z = -78.0
# ----------------------------------------
var randomize_lighting_pos_min_y = 109.0
var randomize_lighting_pos_max_y = 109.0
# ----------------------------------------

# randomize camera | position | fov : done
var randomize_camera_pos = false
var randomize_camera_pos_min_x = -20
var randomize_camera_pos_max_x = 20
var randomize_camera_pos_min_z = -20
var randomize_camera_pos_max_z = 20
# ----------------------------------------
var randomize_camera_pos_min_y = 0
var randomize_camera_pos_max_y = 0
# ----------------------------------------

var randomize_camera_fov = false
var randomize_camera_fov_min = 60
var randomize_camera_fov_max = 90

# randomize marble size, mass, spawn position
var randomize_marble_size = false;
var randomize_marble_min_radius:float=1.5
var randomize_marble_max_radius:float=3.0

var randomize_marble_mass = false; # tested true
var randomize_marble_min_mass:float=4
var randomize_marble_max_mass:float=8

var randomize_marble_pos  = false; # tested true
var randomize_marble_pos_min_x = -40
var randomize_marble_pos_max_x = 40
var randomize_marble_pos_min_z = -40
var randomize_marble_pos_max_z = 40
# ----------------------------------------
var randomize_marble_pos_max_y = 0
var randomize_marble_pos_min_y = 0
# ----------------------------------------


func _ready():
	print("ready")
	_server.connect("client_connected", self, "_connected")
	_server.connect("client_disconnected", self, "_disconnected")
	_server.connect("client_close_request", self, "_close_request")
	#_server.connect("data_received", self, "_on_data")

	var arguments = {}
	for argument in OS.get_cmdline_args():
		if argument.find("=") > -1:
			var key_value = argument.split("=")
			arguments[key_value[0].lstrip("--")] = key_value[1]

	if arguments.has("port"):
		PORT=int(arguments["port"])

	if arguments.has("randomize_background"):
		randomize_background=(int(arguments['randomize_background'])==1)

	if arguments.has("randomize_platform_surface"):
		randomize_platform_surface=(int(arguments['randomize_platform_surface'])==1)

	if arguments.has("randomize_lighting_pos"):
		randomize_lighting_pos=(int(arguments['randomize_lighting_pos'])==1)

	if arguments.has("randomize_camera_pos"):
		randomize_camera_pos=(int(arguments["randomize_camera_pos"])==1)

	# randomize camera fov
	if arguments.has("randomize_camera_fov"):
		randomize_camera_fov=(int(arguments["randomize_camera_fov"])==1)

	# randomize marble size
	if arguments.has("randomize_marble_size"):
		randomize_marble_size=(int(arguments["randomize_marble_size"])==1)

	# randomize marble mass
	if arguments.has("randomize_marble_mass"):
		randomize_marble_mass=(int(arguments["randomize_marble_mass"])==1)

	# randomize marble pos
	if arguments.has("randomize_marble_pos"):
		randomize_marble_pos=(int(arguments["randomize_marble_pos"])==1)

	var err = _server.listen(PORT)
	if err != OK:
		print("Unable to start server")
		set_process(false)
	else:
		print("Running on port=", PORT)
	
func _connected(id, proto):
	print("Client %d connected with protocol: %s" % [id, proto])

func _disconnected(id, was_clean=false):
	print("Client %d disconnected, clean: %s" % [id, str(was_clean)])
	
func _close_request(id, code, reason):
	print("Client %d disconnecting with code: %d, reason: %s" % [id, code, reason])
	
func _process(delta):
	_server.poll()

func send_data(id, data:Dictionary):
	var sendData = JSON.print(data)
	var error:int= _server.get_peer(id).put_packet(sendData.to_utf8())
	if error != OK:
		return true
	return false
