extends Node

signal recieved_request(id, data)

var PORT=9000
var _server=WebSocketServer.new()

var bg_randomized = false

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
		
	if arguments.has("color"):
		bg_randomized=(int(arguments['color'])==1)
	
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


