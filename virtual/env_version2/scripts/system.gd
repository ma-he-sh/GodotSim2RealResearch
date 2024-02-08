extends Spatial

var paused = false

# Called when the node enters the scene tree for the first time.
func _ready():
	pass # Replace with function body.


# Called every frame. 'delta' is the elapsed time since the previous frame.
func _process(delta):
	if Input.is_action_just_pressed("pause"):
		if paused:
			#print("unpaused")
			get_tree().paused = false
			paused = false
		else:
			#print("paused")
			get_tree().paused = true
			paused = true
	if Input.is_action_just_pressed("action_paused"):
		get_tree().paused=true
		print("paused")
		paused=true
	if Input.is_action_just_pressed("action_unpause"):
		get_tree().paused=false
		print("unpaused")
		paused=false
	
