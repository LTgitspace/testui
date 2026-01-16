import tkinter as tk
from tkinter import ttk, messagebox
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
        return self.robot.MoveL(
            desc_pos=desc_pos,
            tool=TOOL_ID,
            user=USER_ID,
            vel=vel,
            ovl=ovl,
            blendR=-1.0
        )

    def stop_motion(self):
        if not self.robot:
            return -1
        return self.robot.StopMotion()

    def get_state(self):
        if self.robot and hasattr(self.robot, 'robot_state_pkg'):
            return self.robot.robot_state_pkg
        return None

