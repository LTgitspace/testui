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
        if not self.robot:
            return -1
        vel = max(1.0, min(100.0, float(vel)))
        ovl = max(1.0, min(100.0, float(ovl)))
        desc_pos = [float(x) for x in desc_pos]
        if len(desc_pos) < 6:
            desc_pos.extend([0.0] * (6 - len(desc_pos)))
        desc_pos = desc_pos[:6]

        try:
            return self.robot.MoveCart(desc_pos, TOOL_ID, USER_ID, vel=vel, acc=0.0, ovl=ovl, blendT=-1.0, config=-1)
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

    def start_jog(self, ref, nb, direction, vel, acc=100.0, max_dis=100.0):
        """
        Safe wrapper for StartJOG that sanitizes inputs to prevent Error 4.
        """
        if not self.robot:
            return -1

        # 1. Sanitize Velocity & Acceleration (0-100)
        vel = max(0.1, min(100.0, float(vel)))
        acc = max(1.0, min(100.0, float(acc)))

        # 2. Sanitize Direction (CRITICAL FIX)
        # The robot only accepts 0 or 1.
        # If you passed -1 (from GUI), this converts it to 0.
        safe_direction = 1 if int(direction) > 0 else 0

        # 3. Sanitize Axis Index
        nb = int(nb)

        try:
            return self.robot.StartJOG(
                int(ref),
                nb,
                safe_direction,
                float(vel),
                float(acc),
                float(max_dis)
            )
        except Exception as e:
            print(f"StartJOG error: {e}")
            return -1

    def stop_jog(self, ref=1):
        if not self.robot:
            return -1
        try:
            return self.robot.StopJOG(int(ref))
        except Exception as e:
            print(f"StopJOG error: {e}")
            return -1

    def imm_stop_jog(self):
        if not self.robot:
            return -1
        try:
            return self.robot.ImmStopJOG()
        except Exception as e:
            print(f"ImmStopJOG error: {e}")
            return -1

    def get_state(self):
        if self.robot and hasattr(self.robot, 'robot_state_pkg'):
            return self.robot.robot_state_pkg
        return None
