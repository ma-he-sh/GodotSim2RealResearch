extends Spatial

const UUID = preload("res://scripts/uuid.gd")
const TEMP_IMG_SAVE_LOC = 'res://temp/save.png'

onready var DROP_BALL=$"Ball/BallObj"
onready var FLOOR=$"Floor/Area"
onready var GlassBedGimbal=$"GlassBed/GlassBed"
onready var GlassBedGimbalMesh=$"GlassBed/GlassBed/GlassBed"
onready var GlassBedGimbalLimitMesh=$"GlassBed/GlassBed/Limit/Limit"
onready var FloorMesh=$"Floor/Area/FloorMesh"
onready var STAT_LABEL=$"STAT"
onready var ACTION_LABEL=$"ACTION"

# ball randomize
var minBRadius:float=1.5
var maxBRadius:float=3.0
var minBWeight:float=4 # was 1.0
var maxBWeight:float=8 # was 4.0
var gravity:float=9.8
var minX:float=-40
var maxX:float=40
var minZ:float=-40
var maxZ:float=40
var minHFB:float=0 # min height from ball
var maxHFB:float=0 # max height from ball

var bedWeight:float=10

var curr_session
const STATUS_STARTED = "STARTED"
const STATUS_ENDED   = "ENDED"
const STATUS_PAUSED  = "PAUSED"

var viewport_camera
var image_data=Image.new()
const IMG_WIDTH=640
const IMG_HEIGHT=360

var yaw = 0.0
var pitch = 0.0
var roll = 0.0
var multiplier = 6.0

var moveAngle = 1.0 * multiplier
var maxMoveAngle = 1.0 * multiplier
var minMoveAngle = -1.0 * multiplier

var init_angles = Vector3(0, 0, 0)
var xAxis = Vector3(1,0,0)
var yAxis = Vector3(0,1,0)
var zAxis = Vector3(0,0,1)

var keypressed = false
var currPitchAngle = 0.0
var currYawAngle=0.0
var currRollAngle=0.0

func get_distance( ball_pos, center_pos ):
	var dist = sqrt( pow( ball_pos.x - center_pos.x, 2) + pow( ball_pos.z - center_pos.z, 2) + pow( ball_pos.y - center_pos.y, 2))
	return dist

func _ready():
	Engine.time_scale=4 # speed of sim
	STAT_LABEL.text=str(Engine.get_frames_per_second())
	
	WebSocketManager._server.connect("data_received", self, "_on_data")
	
	# set camera
	viewport_camera=get_tree().get_root().get_camera()
	
	# randomize color
	var material = GlassBedGimbalMesh.get_surface_material(0)
	material.albedo_color=Color(1, 1, 0)
	GlassBedGimbalMesh.set_surface_material(0, material)
	GlassBedGimbalMesh.set_surface_material(1, material)
	GlassBedGimbalMesh.set_surface_material(2, material)
	GlassBedGimbalLimitMesh.set_surface_material(0, material)
	
	var floorMaterial=FloorMesh.get_surface_material(0)
	if WebSocketManager.bg_randomized:
		var somecolorR = (randi()%200)/200.0
		var somecolorG = (randi()%200)/200.0
		var somecolorB = (randi()%200)/200.0
		floorMaterial.albedo_color=Color(somecolorR, somecolorG, somecolorB)
		FloorMesh.set_surface_material(0, floorMaterial)
	else:
		floorMaterial.albedo_color=Color(0.26, 0.26, 1)
		FloorMesh.set_surface_material(0, floorMaterial)
	
	curr_session=UUID.v4()
	
	# randomize ball size, mass, spawn position
	var randX = rand_range(minX, maxX)
	var randZ = rand_range(minZ, maxZ)
	var randY = rand_range(minHFB, maxHFB)
	var ballPos=Vector3(randX, randY, randZ)
	DROP_BALL.translate(ballPos)
	
	# ball size
	var ballScale = 1.5#rand_range(minBRadius, maxBRadius)
	DROP_BALL.scale=Vector3(ballScale, ballScale, ballScale)
	
	# ball mass
	var ballWeight = rand_range(minBWeight, maxBWeight)
	DROP_BALL.weight=ballWeight

	init_angles = GlassBedGimbal.transform
	STAT_LABEL.text="STARTED"

func _input(event):
	yaw = 0.0
	pitch = 0.0
	roll = 0.0
	
	var current_rotation = GlassBedGimbal.rotation
	var YAW = rad2deg( current_rotation.z )
	var PITCH = rad2deg( current_rotation.x )

	if event is InputEventKey:
		var keyCode = OS.get_scancode_string( event.scancode )
		
		# print(keyCode)
		if keyCode == "Right":
			yaw = minMoveAngle - YAW
			ACTION_LABEL.text="<RIGHT>"
		if keyCode == "Left":
			yaw = maxMoveAngle - YAW
			ACTION_LABEL.text="<LEFT>"
		if keyCode == "Up":
			pitch = minMoveAngle - PITCH
			ACTION_LABEL.text="<UP>"
		if keyCode == "Down":
			pitch = maxMoveAngle - PITCH
			ACTION_LABEL.text="<DOWN>"
		if keyCode == "V":
			reset_pos(1)
		if keyCode == "R":
			get_tree().reload_current_scene()
			
		keypressed=true
		update_angle(yaw, pitch, roll)
		keypressed=false
		
		#print(DROP_BALL.linear_velocity)
		#print(DROP_BALL.translation)
		
		#var ball_distance_from_center = Vector2(DROP_BALL.translation.x, DROP_BALL.translation.z).distance_to(Vector2(0, 0))
		#print(ball_distance_from_center)
		#if ball_distance_from_center <= 20:
		#	print("center")
		#if ball_distance_from_center <= 50:
		#	print("outer")
	
	"""
	if event is InputEventJoypadMotion:
		if event.axis == JOY_AXIS_0:
			if event.axis_value > 0:
				yaw = minMoveAngle - YAW
			else:
				yaw = maxMoveAngle - YAW
		if event.axis == JOY_AXIS_1:
			if event.axis_value > 0:
				pitch = minMoveAngle - PITCH
			else:
				pitch = maxMoveAngle - PITCH
				
		#print(event.axis, " ",event.axis_value)
		keypressed=true
		update_angle(yaw, pitch, roll)
		keypressed=true
	"""

func get_angle(axis, angle):
	var newPos = GlassBedGimbal.global_rotate( axis, angle )

func update_angle(yaw, pitch, roll ):
	#print("yaw=", yaw, " pitch=", pitch, " roll=", roll)
	var yawRad = deg2rad(yaw)
	var pitchRad = deg2rad(pitch)
	var rollRad = deg2rad(roll)
	
	GlassBedGimbal.global_rotate(Vector3(0,0,1), yawRad)
	GlassBedGimbal.global_rotate(Vector3(1,0,0), pitchRad)
	GlassBedGimbal.global_rotate(Vector3(0,1,0), rollRad)
	
func reset_pos(delta):
	currPitchAngle=0.0
	currRollAngle=0.0
	currYawAngle=0.0
	GlassBedGimbal.transform = GlassBedGimbal.transform.interpolate_with( init_angles, 0.8 * delta )

func _process(delta):
	STAT_LABEL.text=str(Engine.get_frames_per_second())
	if keypressed:
		#update_angle(yaw, pitch, roll)
		pass
	else:
		reset_pos(delta)

func get_screenshot():
	var img_data = viewport_camera.get_viewport().get_texture().get_data()
	img_data.flip_y()
	img_data.resize(IMG_WIDTH, IMG_HEIGHT)
	img_data.convert(5) # convert to RGB https://docs.godotengine.org/en/stable/classes/class_image.html#enumerations
	
	#img_data.save_png(TEMP_IMG_SAVE_LOC)
	#var file=File.new()
	#file.open(TEMP_IMG_SAVE_LOC, file.READ)
	#var content = file.get_buffer(file.get_len())
	#file.close()
	
	var base64data = Marshalls.raw_to_base64(img_data.save_png_to_buffer())
	return base64data
	
func _on_data(id):
	yaw = 0.0
	pitch = 0.0
	roll = 0.0
	
	var pkt = WebSocketManager._server.get_peer(id).get_packet()	
	var data = pkt.get_string_from_utf8()
	var parsedData = JSON.parse(data)
	if parsedData.error != OK:
		# data error
		var error = JSON.print({"error": 0, "result": "data_error"})
		WebSocketManager._send_data(id, error.to_utf8())
		
	# get parsed data 
	var res = parsedData.result
	# send the request
	var cmd = res["cmd"]
	var keyCode = res["keycode"]
	
	var current_rotation = GlassBedGimbal.rotation
	var YAW = rad2deg( current_rotation.z )
	var PITCH = rad2deg( current_rotation.x )
	var ROLL  = rad2deg( current_rotation.y )
	
	if cmd == "state":
		if keyCode == "Right":
			yaw = minMoveAngle - YAW
			ACTION_LABEL.text="<RIGHT>"
		if keyCode == "Left":
			yaw = maxMoveAngle - YAW
			ACTION_LABEL.text="<LEFT>"
		if keyCode == "Up":
			pitch = minMoveAngle - PITCH
			ACTION_LABEL.text="<UP>"
		if keyCode == "Down":
			pitch = maxMoveAngle - PITCH
			ACTION_LABEL.text="<DOWN>"
		if keyCode == "V":
			reset_pos(1)
		if keyCode == "R":
			#get_tree().change_scene("res://sim_env.tscn")
			get_tree().reload_current_scene()
			
		keypressed=true
		update_angle(yaw, pitch, roll)
		keypressed=false
	if cmd == "reset":
		#get_tree().change_scene("res://sim_env.tscn")
		get_tree().reload_current_scene()
		
	var ball_distance_from_center = Vector2(DROP_BALL.translation.x, DROP_BALL.translation.z).distance_to(Vector2(0, 0))
		
	var screenshot = get_screenshot()
	#print(screenshot)
	var payload = {
		"error": 200,
		"result": {
			"yaw": yaw,
			"pitch": pitch,
			"roll": roll,
			"ball_pos": {
				"x": DROP_BALL.translation.x,
				"y": DROP_BALL.translation.z
			},
			"ball_velocity": {
				"x": DROP_BALL.linear_velocity.x,
				"y": DROP_BALL.linear_velocity.z
			},
			"in_center": ball_distance_from_center <= 20,
			"in_outer" : ball_distance_from_center <= 50,
			"dist_to_center": ball_distance_from_center,
			"img" : screenshot,
			"prev_data": {
				"yaw": YAW,
				"pitch": PITCH,
				"roll" : ROLL,
			}
		}
	}
	
	WebSocketManager.send_data(id, payload)
