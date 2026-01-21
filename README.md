# Cobot 6-DOF Control

A Python-based graphical user interface for controlling a Fairino FR3 collaborative robot with 6-DOF (degree of freedom) Cartesian movement and jogging control using the Fairino Robot SDK.

## Overview

This application provides an intuitive interface to control a Fairino cobot with the following capabilities:

- Connect to the robot controller via network
- Control robot position along X, Y, and Z axes with configurable constraints
- Control robot rotation using Rx, Ry, and Rz (Euler angles)
- Adjust velocity and overdrive parameters in real-time
- Monitor robot state and current position/rotation feedback
- Emergency stop functionality
- Move to home position
- Reset joints to predefined positions
- Jogging control for fine manual movements along any axis
- Real-time robot state monitoring

## Requirements

- Python 3.8 or higher
- Tkinter (usually included with Python)
- Network connection to the Fairino cobot controller

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd testui
```

2. Create a virtual environment (optional but recommended):
```bash
python -m venv .venv
```

3. Activate the virtual environment:
   - On Windows:
   ```bash
   .venv\Scripts\activate
   ```
   - On Linux/Mac:
   ```bash
   source .venv/bin/activate
   ```

## Usage

Start the application:
```bash
python main.py
```

### GUI Panels

1. **Connection Panel**: 
   - Enter the robot IP address
   - Click "Connect" to establish connection
   - Status indicator shows connection state

2. **Position & Rotation Control Panel**:
   - Position Control: X, Y, Z sliders for Cartesian position (mm)
   - Rotation Control: Rx, Ry, Rz sliders for Euler angles (degrees)
   - Each slider shows current value and configured range

3. **Movement Control Panel**:
   - Velocity: Control movement speed (1-100%)
   - Overdrive: Control force/power (1-100%)
   - Buttons:
     - Move to Position: Execute movement to current slider positions
     - Stop Motion: Emergency stop
     - Home Position: Return to home position
     - Reset Joints: Reset to predefined joint positions

4. **Jogging Control Panel**:
   - Select axis to jog (X, Y, Z, Rx, Ry, Rz)
   - Set jog velocity and overdrive
   - Buttons:
     - Jog +: Move positive direction
     - Jog -: Move negative direction
     - Stop Jog: Stop jogging motion

5. **Robot Status Panel**:
   - Current Position: Displays real-time X, Y, Z, Rx, Ry, Rz values
   - Robot State: Connection and operational status

### Configuration

Edit `src/config.py` to customize:

- Robot IP address and port (DEFAULT_ROBOT_IP, DEFAULT_ROBOT_PORT)
- Position constraints for X, Y, Z axes (AXIS_CONSTRAINTS)
- Rotation constraints for Rx, Ry, Rz (ROTATION_CONSTRAINTS)
- Default velocity and overdrive (DEFAULT_VELOCITY, DEFAULT_OVERDRIVE)
- Velocity/overdrive range limits (MIN_VELOCITY, MAX_VELOCITY, MIN_OVERDRIVE, MAX_OVERDRIVE)
- Reset motion parameters (RESET_VELOCITY, RESET_OVERDRIVE, RESET_JOINTS_POSITION)
- Home position target (HOME_POSITION)
- Monitoring interval (MONITOR_THREAD_INTERVAL)

## Project Structure

```
testui/
├── main.py                      # Application entry point
├── requirements.txt             # Python dependencies
├── README.md                    # This file
├── src/
│   ├── __init__.py
│   ├── config.py               # Configuration constants
│   ├── gui.py                  # Tkinter GUI implementation
│   ├── util.py                 # Robot connection utilities
│   ├── constraint_frame.py      # Position/rotation control widget
│   └── testpoint.py             # Test point definitions
├── fairino/
│   ├── __init__.py
│   ├── robot_sdk_core.py        # Fairino Robot SDK
│   └── robot_sdk_core.c         # SDK C extension
└── .gitignore
```

## Configuration Details

### Position Constraints (AXIS_CONSTRAINTS)
Define position limits for each Cartesian axis:
```python
AXIS_CONSTRAINTS = {
    'X': {'min': -500, 'max': 500, 'current': 0},
    'Y': {'min': -200, 'max': 200, 'current': 0},
    'Z': {'min': 400, 'max': 700, 'current': 550}
}
```

### Rotation Constraints (ROTATION_CONSTRAINTS)
Define rotation limits for each axis:
```python
ROTATION_CONSTRAINTS = {
    'Rx': {'min': -180, 'max': 180, 'current': 0},
    'Ry': {'min': -180, 'max': 180, 'current': 0},
    'Rz': {'min': -180, 'max': 180, 'current': 0}
}
```

### Motion Parameters
- `DEFAULT_VELOCITY`: Initial movement speed (1-100%)
- `DEFAULT_OVERDRIVE`: Initial overdrive percentage (1-100%)
- `MIN_VELOCITY` / `MAX_VELOCITY`: Velocity range limits
- `MIN_OVERDRIVE` / `MAX_OVERDRIVE`: Overdrive range limits
- `RESET_VELOCITY`: Speed for reset motion
- `RESET_OVERDRIVE`: Overdrive for reset motion
- `RESET_JOINTS_POSITION`: Target joint angles for reset

### Connection Settings
- `DEFAULT_ROBOT_IP`: Robot controller IP address (default: 192.168.58.2)
- `DEFAULT_ROBOT_PORT`: RPC port (default: 20003)
- `TOOL_ID`: Tool identifier (default: 0)
- `USER_ID`: User identifier (default: 0)

## Key Features

### Multi-Axis Control
- Full 6-DOF control with separate position and rotation parameters
- Independent constraints for position and rotation
- Real-time feedback of all axes

### Jogging Interface
- Fine manual control of any axis
- Configurable jog velocity and overdrive
- Smooth start/stop motion

### Thread-Safe Operation
- Background monitoring thread for robot state updates
- Safe GUI updates using Tkinter scheduling
- Prevents GUI freezing during robot operations

### Error Handling
- Connection verification
- Motion error reporting
- Graceful error display in message boxes
- Robot state validation

## Robot SDK Methods

This application utilizes the Fairino Robot SDK:

- `MoveCart()`: Cartesian movement with position and rotation
- `MoveJ()`: Joint space movement
- `StopMotion()`: Emergency stop
- `GetControllerIP()`: Connection verification
- `robot_state_pkg`: Real-time robot state feedback

## Troubleshooting

### Connection Issues
- Verify the robot IP address is correct
- Check network connectivity to the robot controller
- Ensure the robot controller is powered on and accessible
- Verify network ports are not blocked

### Movement Errors
- Confirm target position is within configured constraints
- Check if robot is in appropriate mode
- Verify no emergency stop or safety limits are triggered
- Monitor error messages in the message box

### Position Out of Safe Range
- Verify position values are within AXIS_CONSTRAINTS limits
- Check rotation values are within ROTATION_CONSTRAINTS limits
- Review configured min/max values in config.py

### GUI Responsiveness
- Monitor thread is running continuously
- Check system resources and available memory
- Ensure robot connection is stable

## Development

### Adding New Features
1. Define new parameters in `src/config.py`
2. Create utility methods in `src/util.py`
3. Add GUI elements in `src/gui.py`
4. Update constraint frames if needed in `src/constraint_frame.py`

### Modifying Constraints
Edit `src/config.py` to change:
- Axis limits via AXIS_CONSTRAINTS
- Rotation limits via ROTATION_CONSTRAINTS
- Motion speeds via RESET_VELOCITY and velocity parameters

## License

Specify your license here

