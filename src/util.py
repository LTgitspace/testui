from src.config import *


class RobotConnection:
    def __init__(self):
        self.robot = None
        self.is_connected = False
        self.robot_state_pkg = None

    def connect(self, ip):
        try:
            from fairino.robot_sdk_core import RPC
            self.robot = RPC(ip)
            error, _ = self.robot.GetControllerIP()

            if error == 0:
                self.is_connected = True
                return True, "Connected successfully"
            else:
                return False, f"Connection failed with error {error}"
        except Exception as e:
            return False, str(e)

    def disconnect(self):
        self.is_connected = False
        self.robot = None

    def move_l(self, desc_pos, vel, ovl):
        if not self.robot or not hasattr(self.robot, 'robot'):
            return -1
        vel = max(1.0, min(100.0, float(vel)))
        ovl = max(1.0, min(100.0, float(ovl)))
        desc_pos = [float(x) for x in desc_pos]
        if len(desc_pos) < 6:
            desc_pos.extend([0.0] * (6 - len(desc_pos)))
        desc_pos = desc_pos[:6]

        try:
            return self.robot.robot.MoveCart(
                desc_pos,
                int(TOOL_ID),
                int(USER_ID),
                float(vel),
                0.0,
                float(ovl),
                -1.0,
                int(-1)
            )
        except Exception as e:
            print(f"MoveCart error: {e}")
            return -1

    def move_j(self, joint_pos, vel, ovl):
        if not self.robot:
            return -1
        vel = max(1.0, min(100.0, float(vel)))
        ovl = max(1.0, min(100.0, float(ovl)))
        joint_pos = [float(x) for x in joint_pos]
        return self.robot.MoveJ(joint_pos, TOOL_ID, USER_ID, vel=vel, ovl=ovl)

    def stop_motion(self):
        if not self.robot:
            return -1
        return self.robot.StopMotion()

    def get_state(self):
        if self.robot and hasattr(self.robot, 'robot_state_pkg'):
            return self.robot.robot_state_pkg
        return None

