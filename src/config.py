WINDOW_TITLE = "Cobot 3-Axis Control"
WINDOW_WIDTH = 900
WINDOW_HEIGHT = 700
WINDOW_BG = '#f0f0f0'

DEFAULT_ROBOT_IP = "192.168.58.2"
DEFAULT_ROBOT_PORT = 20003

AXIS_CONSTRAINTS = {
    'X': {'min': -200, 'max': 200, 'current': 0},
    'Y': {'min': -200, 'max': 200, 'current': 0},
    'Z': {'min': 50, 'max': 200, 'current': 100}
}

DEFAULT_POSITION = {'X': 0, 'Y': 0, 'Z': 100}
HOME_POSITION = [0.0, 0.0, 100.0, 0.0, 0.0, 0.0]

DEFAULT_VELOCITY = 20
DEFAULT_OVERDRIVE = 100
MIN_VELOCITY = 1
MAX_VELOCITY = 100
MIN_OVERDRIVE = 1
MAX_OVERDRIVE = 100

RESET_VELOCITY = 5   # Very slow safety speed for reset
RESET_OVERDRIVE = 20 # Low power for reset
# The robot moves to this Cartesian position AFTER unwinding joints
# Format: [X, Y, Z, Rx, Ry, Rz] (Units: mm, degrees)
# Matches the "Cartesian" or "Base" coordinates in the Web UI.
HOME_POSITION = [0.0, 0.0, 100.0, 0.0, 0.0, 0.0]

# The robot moves to these joint angles FIRST to untwist (Candlestick pose)
# Format: [J1, J2, J3, J4, J5, J6] (Units: degrees)
# Matches the "Joint" angles (J1-J6) in the Web UI.
RESET_JOINTS_POSITION = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]

MONITOR_THREAD_INTERVAL = 0.5
TOOL_ID = 0
USER_ID = 0

