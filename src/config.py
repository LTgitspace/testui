WINDOW_TITLE = "Cobot 6-DOF Control"
WINDOW_WIDTH = 900
WINDOW_HEIGHT = 1000
WINDOW_BG = '#f0f0f0'

DEFAULT_ROBOT_IP = "192.168.58.2"
DEFAULT_ROBOT_PORT = 20003

AXIS_CONSTRAINTS = {
    'X': {'min': -500, 'max': 500, 'current': 0},
    'Y': {'min': -200, 'max': 200, 'current': 0},
    'Z': {'min': 400, 'max': 700, 'current': 550}
}

ROTATION_CONSTRAINTS = {
    'Rx': {'min': -180, 'max': 180, 'current': 0},
    'Ry': {'min': -180, 'max': 180, 'current': 0},
    'Rz': {'min': -180, 'max': 180, 'current': 0}
}

DEFAULT_POSITION = {'X': 0, 'Y': 0, 'Z': 550}
DEFAULT_ROTATION = {'Rx': 0.0, 'Ry': 0.0, 'Rz': 0.0}

HOME_POSITION = [0.0, 0.0, 600.0, 0.0, 0.0, 0.0]

DEFAULT_VELOCITY = 20
DEFAULT_OVERDRIVE = 100
MIN_VELOCITY = 1
MAX_VELOCITY = 100
MIN_OVERDRIVE = 1
MAX_OVERDRIVE = 100

RESET_VELOCITY = 50
RESET_OVERDRIVE = 20

RESET_JOINTS_POSITION = [0.0, -90.0, 90.0, -90.0, -90.0, 0.0]

MONITOR_THREAD_INTERVAL = 0.5
TOOL_ID = 0
USER_ID = 0

