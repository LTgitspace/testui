import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.util import RobotConnection
from src.config import DEFAULT_ROBOT_IP, DEFAULT_VELOCITY, DEFAULT_OVERDRIVE


def move_to_test_point():
    connection = RobotConnection()
    success, message = connection.connect(DEFAULT_ROBOT_IP)

    if not success:
        print(f"Connection failed: {message}")
        return False

    print("Connected to robot successfully")

    test_position = [-600.0, 0.0, 700.0, 180.0, 0.0, 90.0]
    test_joint_angles = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]

    print(f"Moving to test point: X: -600mm, Y: 0mm, Z: 700mm, rX: 180, rY: 0, rZ: 90")

    try:
        error = connection.robot.robot.MoveCart(
            test_position,
            int(0),
            int(0),
            float(DEFAULT_VELOCITY),
            0.0,
            float(DEFAULT_OVERDRIVE),
            -1.0,
            int(-1)
        )

        if error == 0:
            print("Successfully moved to test point!")
            return True
        else:
            print(f"Movement failed with error code: {error}")
            return False
    except Exception as e:
        print(f"Error: {e}")
        return False


if __name__ == "__main__":
    move_to_test_point()


