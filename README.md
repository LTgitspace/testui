# Cobot 3-Axis Control

A Python-based graphical user interface for controlling a collaborative robot (cobot) with 3-axis Cartesian movement using the Fairino Robot SDK.

## Overview

This application provides a user-friendly interface to control a Fairino cobot with the following capabilities:

- Connect to the robot controller via network
- Move the robot along X, Y, and Z axes with configurable position constraints
- Adjust velocity and overdrive parameters in real-time
- Monitor robot state and position feedback
- Emergency stop functionality
- Home position return
- Joint reset to zero position
- Smooth motion with blended trajectory control

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

4. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

Start the application:
```bash
python main.py
```

### GUI Controls

1. **Connection Panel**: Enter the robot IP address and click "Connect" to establish connection
2. **Axis Controls**: Use sliders to adjust X, Y, Z positions within configured limits
3. **Velocity Control**: Adjust movement velocity (1-100)
4. **Overdrive Control**: Adjust overdrive percentage (1-100)
5. **Movement Buttons**:
   - Move to Position: Execute movement to current slider position
   - Stop Motion: Emergency stop
   - Home Position: Return to home pose
   - Reset Joints: Reset all joints to zero position slowly

### Configuration

Edit `src/config.py` to customize:

- Robot IP address and port
- Axis position constraints (min/max values)
- Default velocity and overdrive settings
- Reset motion parameters
- Window size and appearance

## Project Structure

```
testui/
├── main.py                      # Application entry point
├── requirements.txt             # Python dependencies
├── src/
│   ├── __init__.py
│   ├── config.py               # Configuration constants
│   ├── gui.py                  # Tkinter GUI implementation
│   ├── util.py                 # Robot connection utilities
│   └── constraint_frame.py      # Constraint configuration widget
├── fairino/
│   ├── __init__.py
│   ├── robot_sdk_core.py        # Fairino Robot SDK
│   └── robot_sdk_core.c         # SDK C extension
└── README.md
```

## Key Features

### Thread-Safe GUI Updates
The application uses thread-safe methods to update the GUI from background robot monitoring threads, preventing freezing or crashes.

### Motion Smoothing
Trajectory blending (blendR=5.0) is enabled for smooth, continuous robot motion.

### Safety Constraints
- Z-axis minimum clearance of 50mm to prevent collisions
- Configurable velocity limits for safer operation
- Reset motion at reduced velocity (5mm/s) for smooth positioning

### Real-Time Monitoring
Background monitoring thread updates robot state information including:
- Current joint positions
- Tool position and orientation
- Robot state and mode
- Error codes and collision detection

## Configuration Details

### AXIS_CONSTRAINTS
Define position limits for each axis:
```python
AXIS_CONSTRAINTS = {
    'X': {'min': -200, 'max': 200, 'current': 0},
    'Y': {'min': -200, 'max': 200, 'current': 0},
    'Z': {'min': 50, 'max': 200, 'current': 100}
}
```

### Motion Parameters
- `DEFAULT_VELOCITY`: Initial movement speed (mm/s)
- `DEFAULT_OVERDRIVE`: Initial overdrive percentage (0-100)
- `RESET_VELOCITY`: Speed for reset motion (mm/s)
- `HOME_POSITION`: Target position for home command

### Connection Settings
- `DEFAULT_ROBOT_IP`: Robot controller IP address
- `DEFAULT_ROBOT_PORT`: RPC port (typically 20003)

## Error Handling

The application includes error handling for:
- Connection failures with descriptive error messages
- Robot motion errors displayed in the message box
- Network timeouts and disconnections
- Invalid position constraints

## Robot SDK

This application utilizes the Fairino Robot SDK with the following key methods:

- `MoveL()`: Linear movement to specified position
- `StopMotion()`: Emergency stop
- `GetControllerIP()`: Connection verification
- `robot_state_pkg`: Real-time robot state feedback

## Troubleshooting

### Connection Issues
- Verify the robot IP address is correct
- Check network connectivity to the robot controller
- Ensure the robot controller is powered on and accessible

### Movement Errors
- Confirm target position is within configured constraints
- Check if robot is in appropriate mode (automatic vs manual)
- Verify no emergency stop or safety limits are triggered

### GUI Freezing
- Ensure the connection is active and responsive
- Check system resources and available memory
- Restart the application if needed

## Development

### Adding New Features
1. Create new utility methods in `src/util.py`
2. Add GUI elements in `src/gui.py`
3. Update configuration in `src/config.py` as needed

### Modifying Constraints
Edit `src/config.py` to change axis limits, velocity ranges, or default values.

## License

[Specify your license here]

## Support

For issues or questions, please contact the development team or create an issue in the repository.

