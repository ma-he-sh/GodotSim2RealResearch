from dotenv import dotenv_values
import numpy as np

ENV=dotenv_values(".env")

# CSV PATH
CSV_PATH=ENV['CSV_PATH']

# Servo config
MIN_PULSE=float(ENV['MIN_PULSE'])
MAX_PULSE=float(ENV['MAX_PULSE'])
MIN_ANGLE=float(ENV['MIN_ANGLE'])
MAX_ANGLE=float(ENV['MAX_ANGLE'])
MIN_RANGE=float(ENV['MIN_RANGE'])
MAX_RANGE=float(ENV['MAX_RANGE'])

X_PWM=int(ENV['X_PWM'])
Y_PWM=int(ENV['Y_PWM'])
Z_PWM=int(ENV['Z_PWM'])

# Camera config
CAM_SOURCE=int(ENV['CAM_SOURCE'])
CAM_WIDTH=int(ENV['CAM_WIDTH'])
CAM_HEIGHT=int(ENV['CAM_HEIGHT'])
CAM_FPS=int(ENV['CAM_FPS'])
DOWNSCALE_RATIO=CAM_WIDTH/CAM_HEIGHT
CR_HEIGHT=80
CR_WIDTH=int(CR_HEIGHT*DOWNSCALE_RATIO)
NUM_CHANNELS=3 # RGB

input_shape = ( CR_HEIGHT, CR_HEIGHT, NUM_CHANNELS )

# Logging config
LOGGING_PATH=ENV['LOGGING_PATH']

# PORT CONNECTION
EXEC_PATH=ENV['EXEC_PATH']
EXEC_ENV =ENV['EXEC_ENV']
ENV_1_PORT=int(ENV['ENV_1_PORT'])
ENV_2_PORT=int(ENV['ENV_2_PORT'])
ENV_3_PORT=int(ENV['ENV_3_PORT'])
ENV_4_PORT=int(ENV['ENV_4_PORT'])

# PHYSICAL ENVIRONMENT
INITIAL_HEIGHT=float(ENV['INITIAL_HEIGHT'])
BASE_RADIUS=float(ENV['BASE_RADIUS'])
PLATFORM_RADIUS=float(ENV['PLATFORM_RADIUS'])
SERVO_HORN_LENGTH=float(ENV['SERVO_HORN_LENGTH'])
SERVO_LEG_LENGTH=float(ENV['SERVO_LEG_LENGTH'])

BASE_ANGLE_X=float(ENV['BASE_ANGLE_X'])
BASE_ANGLE_Y=float(ENV['BASE_ANGLE_Y'])
BASE_ANGLE_Z=float(ENV['BASE_ANGLE_Z'])
# platform angles :: position arms connecting to the platforms : angles
PLATFORM_ANGLE_X=float(ENV['PLATFORM_ANGLE_X'])
PLATFORM_ANGLE_Y=float(ENV['PLATFORM_ANGLE_Y'])
PLATFORM_ANGLE_Z=float(ENV['PLATFORM_ANGLE_Z'])
# beta angles :: angles of the arm to connected base
BETA_ANGLES_X=0.0
BETA_ANGLES_Y=2*np.pi/3
BETA_ANGLES_Z=-2*np.pi/3

# Serial data
SERIAL_PORT=ENV['SERIAL_PORT']
SERIAL_BAUDRATE=int(ENV['SERIAL_BAUDRATE'])
SERIAL_TIMEOUT=float(ENV['SERIAL_TIMEOUT'])

sys_config = {
    'path' : {
        'csv_path': CSV_PATH
    },
    'servo': {
        'x_pwm': X_PWM,
        'y_pwm': Y_PWM,
        'z_pwm': Z_PWM,
        'min_angle': MIN_ANGLE,
        'max_angle': MAX_ANGLE,
        'min_pulse': MIN_PULSE,
        'max_pulse': MAX_PULSE,
        'min_range': MIN_RANGE,
        'max_range': MAX_RANGE
    },
    'camera': {
        'source': CAM_SOURCE,           # camer source
        'cap_width': CAM_WIDTH,         # cap width
        'cap_height': CAM_HEIGHT,       # cap height
        'cap_fps': CAM_FPS,             # cap fps
        'cr_width': CR_WIDTH,           # crop width
        'cr_height': CR_HEIGHT,         # crop height
        'scale_ratio': DOWNSCALE_RATIO  # downscale ratio
    },
    'virtual': {
        'exec_path': EXEC_PATH,
        'exec_env' : EXEC_ENV,
        'rand_bg'  : 1, #randomize bg,
        'add_noise': 0, # randomize noise
        'env1_port': ENV_1_PORT,
        'env2_port': ENV_2_PORT,
        'env3_port': ENV_3_PORT,
        'env4_port': ENV_4_PORT,
        'cap_width': CAM_WIDTH,
        'cap_height': CAM_HEIGHT,
        'cr_width' : CR_WIDTH,
        'cr_height': CR_HEIGHT,
        'scale_ratio': DOWNSCALE_RATIO
    },
    'physical': {
        'INITIAL_HEIGHT': INITIAL_HEIGHT,
        'BASE_RADIUS': BASE_RADIUS,
        'PLATFORM_RADIUS': PLATFORM_RADIUS,
        'SERVO_HORN_LENGTH': SERVO_HORN_LENGTH,
        'SERVO_LEG_LENGTH': SERVO_LEG_LENGTH,
        'BASE_ANGLE_X': BASE_ANGLE_X,
        'BASE_ANGLE_Y': BASE_ANGLE_Y,
        'BASE_ANGLE_Z': BASE_ANGLE_Z,
        'PLATFORM_ANGLE_X': PLATFORM_ANGLE_X,
        'PLATFORM_ANGLE_Y': PLATFORM_ANGLE_Y,
        'PLATFORM_ANGLE_Z': PLATFORM_ANGLE_Z,
        'BETA_ANGLES_X': BETA_ANGLES_X,
        'BETA_ANGLES_Y': BETA_ANGLES_Y,
        'BETA_ANGLES_Z': BETA_ANGLES_Z,
    },
    'serial': {
        'SERIAL_PORT': SERIAL_PORT,
        'SERIAL_BAUDRATE': SERIAL_BAUDRATE,
        'SERIAL_TIMEOUT' : SERIAL_TIMEOUT,
    }
}
