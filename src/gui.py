import tkinter as tk
from tkinter import ttk, messagebox
from src.config import *
from src.constraint_frame import ConstraintFrame
from src.config import HOME_POSITION


class CobotControlGUI:
    def __init__(self, root):
        self.root = root
        self.root.title(WINDOW_TITLE)
        self.root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.root.configure(bg=WINDOW_BG)

        self.connection = None
        self.monitoring_thread = None
        self.stop_monitoring = False

        self.axis_constraints = {k: v.copy() for k, v in AXIS_CONSTRAINTS.items()}
        self.current_pos = DEFAULT_POSITION.copy()

        self.constraint_frames = {}
        self.velocity_var = tk.IntVar(value=DEFAULT_VELOCITY)
        self.overdrive_var = tk.IntVar(value=DEFAULT_OVERDRIVE)
        self.ip_var = tk.StringVar(value=DEFAULT_ROBOT_IP)

        self.status_label = None
        self.connect_btn = None
        self.move_btn = None
        self.stop_btn = None
        self.home_btn = None
        self.reset_btn = None
        self.pos_label = None
        self.state_label = None
        self.info_label = None
        self.vel_label = None
        self.ovl_label = None

        self.create_widgets()

    def create_widgets(self):
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        self._create_connection_frame(main_frame)
        self._create_control_frame(main_frame)
        self._create_movement_frame(main_frame)
        self._create_status_frame(main_frame)

        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)

    def _create_connection_frame(self, parent):
        conn_frame = ttk.LabelFrame(parent, text="Connection", padding="10")
        conn_frame.grid(row=0, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)

        ttk.Label(conn_frame, text="Robot IP:").grid(row=0, column=0, padx=5)
        ip_entry = ttk.Entry(conn_frame, textvariable=self.ip_var, width=20)
        ip_entry.grid(row=0, column=1, padx=5)

        self.connect_btn = ttk.Button(conn_frame, text="Connect", command=self.connect_robot)
        self.connect_btn.grid(row=0, column=2, padx=5)

        self.status_label = ttk.Label(conn_frame, text="Status: Disconnected", foreground="red")
        self.status_label.grid(row=0, column=3, padx=10)

    def _create_control_frame(self, parent):
        control_frame = ttk.LabelFrame(parent, text="3-Axis Control (mm)", padding="15")
        control_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)

        for idx, axis in enumerate(['X', 'Y', 'Z']):
            constraint_frame = ConstraintFrame(
                control_frame,
                axis,
                self.axis_constraints,
                self.update_info
            )
            constraint_frame.get_frame().grid(row=idx, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=8)
            self.constraint_frames[axis] = constraint_frame

    def _create_movement_frame(self, parent):
        move_frame = ttk.LabelFrame(parent, text="Movement Control", padding="10")
        move_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)

        ttk.Label(move_frame, text="Velocity (%):").grid(row=0, column=0, padx=5)
        vel_scale = ttk.Scale(move_frame, from_=MIN_VELOCITY, to=MAX_VELOCITY, variable=self.velocity_var, orient=tk.HORIZONTAL)
        vel_scale.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=5)
        self.vel_label = ttk.Label(move_frame, text=f"{DEFAULT_VELOCITY}%", width=4)
        self.vel_label.grid(row=0, column=2, padx=5)
        self.velocity_var.trace_add('write', self._update_vel_label)

        ttk.Label(move_frame, text="Overdrive (%):").grid(row=1, column=0, padx=5)
        ovl_scale = ttk.Scale(move_frame, from_=MIN_OVERDRIVE, to=MAX_OVERDRIVE, variable=self.overdrive_var, orient=tk.HORIZONTAL)
        ovl_scale.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=5)
        self.ovl_label = ttk.Label(move_frame, text=f"{DEFAULT_OVERDRIVE}%", width=4)
        self.ovl_label.grid(row=1, column=2, padx=5)
        self.overdrive_var.trace_add('write', self._update_ovl_label)

        btn_frame = ttk.Frame(move_frame)
        btn_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)

        self.move_btn = ttk.Button(btn_frame, text="Move to Position", command=self.move_to_position, state=tk.DISABLED)
        self.move_btn.pack(side=tk.LEFT, padx=5)

        self.stop_btn = ttk.Button(btn_frame, text="Stop Motion", command=self.stop_motion, state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT, padx=5)

        self.home_btn = ttk.Button(btn_frame, text="Home Position", command=self.move_to_home, state=tk.DISABLED)
        self.home_btn.pack(side=tk.LEFT, padx=5)

        self.reset_btn = ttk.Button(btn_frame, text="Reset Joints (0,0,0)", command=self.move_to_reset, state=tk.DISABLED)
        self.reset_btn.pack(side=tk.LEFT, padx=5)

        move_frame.columnconfigure(1, weight=1)

    def _create_status_frame(self, parent):
        status_frame = ttk.LabelFrame(parent, text="Robot Status", padding="10")
        status_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)

        ttk.Label(status_frame, text="Current Position (mm):").grid(row=0, column=0, sticky=tk.W, padx=5)
        self.pos_label = ttk.Label(status_frame, text=f"X: {DEFAULT_POSITION['X']:.2f}  Y: {DEFAULT_POSITION['Y']:.2f}  Z: {DEFAULT_POSITION['Z']:.2f}", font=("Arial", 11, "bold"))
        self.pos_label.grid(row=0, column=1, sticky=tk.W, padx=5)

        ttk.Label(status_frame, text="Robot State:").grid(row=1, column=0, sticky=tk.W, padx=5)
        self.state_label = ttk.Label(status_frame, text="Ready", foreground="green", font=("Arial", 10, "bold"))
        self.state_label.grid(row=1, column=1, sticky=tk.W, padx=5)

        ttk.Label(status_frame, text="Info:").grid(row=2, column=0, sticky=tk.W, padx=5)
        self.info_label = ttk.Label(status_frame, text="No information", foreground="blue")
        self.info_label.grid(row=2, column=1, sticky=tk.W, padx=5)

    def connect_robot(self):
        if self.connection and self.connection.is_connected:
            self.disconnect_robot()
            return

        ip = self.ip_var.get()
        if not ip:
            messagebox.showerror(
                "Missing IP Address",
                "Please enter a valid robot IP address.\n\n"
                "Example: 192.168.58.2\n\n"
                "Check your robot's network configuration if unsure."
            )
            return

        try:
            from src.util import RobotConnection
            self.connection = RobotConnection()
            self.update_info("Connecting to robot...")
            self.root.update()

            success, message = self.connection.connect(ip)

            if success:
                self.status_label.config(text="Status: Connected", foreground="green")
                self.connect_btn.config(text="Disconnect")
                self.move_btn.config(state=tk.NORMAL)
                self.stop_btn.config(state=tk.NORMAL)
                self.home_btn.config(state=tk.NORMAL)
                self.reset_btn.config(state=tk.NORMAL)

                self.update_info("Resetting to safe position...")
                self.root.update()

                self.reset_joints()

                self.update_info("Connected successfully!")

                self.stop_monitoring = False
                import threading
                self.monitoring_thread = threading.Thread(target=self.monitor_robot, daemon=True)
                self.monitoring_thread.start()
            else:
                messagebox.showerror(
                    "Connection Failed",
                    f"Could not connect to robot at {ip}\n\n"
                    f"Details: {message}\n\n"
                    f"Please check:\n"
                    f"- Robot IP address is correct\n"
                    f"- Robot is powered on\n"
                    f"- Network connection is active"
                )
                self.update_info("Connection failed")
        except Exception as e:
            messagebox.showerror(
                "Connection Error",
                f"An error occurred while connecting:\n\n{str(e)}\n\n"
                f"Please verify the robot IP and network settings."
            )
            self.update_info(f"Error: {str(e)}")

    def disconnect_robot(self):
        self.stop_monitoring = True
        if self.connection:
            self.connection.disconnect()
            self.connection = None

        self.status_label.config(text="Status: Disconnected", foreground="red")
        self.connect_btn.config(text="Connect")
        self.move_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.DISABLED)
        self.home_btn.config(state=tk.DISABLED)
        self.reset_btn.config(state=tk.DISABLED)

        self.update_info("Disconnected from robot")

    def monitor_robot(self):
        import time
        while not self.stop_monitoring and self.connection and self.connection.is_connected:
            try:
                state_pkg = self.connection.get_state()
                if state_pkg:
                    state_text = ""
                    state_color = "black"

                    if state_pkg.robot_state == 1:
                        state_text = "Idle"
                        state_color = "green"
                    elif state_pkg.robot_state == 2:
                        state_text = "Moving"
                        state_color = "orange"
                    elif state_pkg.robot_state == 3:
                        state_text = "Paused"
                        state_color = "blue"
                    else:
                        state_text = f"State: {state_pkg.robot_state}"
                        state_color = "black"

                    self.root.after(0, lambda t=state_text, c=state_color: self.state_label.config(text=t, foreground=c))

                time.sleep(MONITOR_THREAD_INTERVAL)
            except Exception as e:
                pass

    def reset_joints(self):
        if not self.connection or not self.connection.is_connected:
            return

        try:
            self.update_info("Resetting joints to 0 position (Unwinding)...")
            self.root.update()

            # 1. Unwind to Zero Joints (Safe High/Candlestick)
            # Use very slow velocity from config
            error = self.connection.move_j(RESET_JOINTS_POSITION, RESET_VELOCITY, RESET_OVERDRIVE)

            if error == 0:
                self.update_info("Joints reset. Moving to Home Position...")
                # Allow some time for motion to settle/start
                import time
                time.sleep(0.5)

                # 2. Move to Home Position (Cartesian)
                # We use MoveL to go straight to the working height safely.
                error = self.connection.move_l(HOME_POSITION, RESET_VELOCITY, RESET_OVERDRIVE)

                if error == 0:
                    time.sleep(0.5)

                    self.constraint_frames['X'].set_value(HOME_POSITION[0])
                    self.constraint_frames['Y'].set_value(HOME_POSITION[1])
                    self.constraint_frames['Z'].set_value(HOME_POSITION[2])

                    self.current_pos['X'] = HOME_POSITION[0]
                    self.current_pos['Y'] = HOME_POSITION[1]
                    self.current_pos['Z'] = HOME_POSITION[2]

                    self.root.after(0, lambda: self.pos_label.config(
                         text=f"X: {HOME_POSITION[0]:.2f}  Y: {HOME_POSITION[1]:.2f}  Z: {HOME_POSITION[2]:.2f}"
                    ))
                    self.update_info("Reset Complete: Robot at Home Position")
                else:
                    self.update_info(f"Reset Partial: Unwound to 0, but Home Move Failed ({error})")
            else:
                self.update_info(f"Joint reset failed with error {error}")
        except Exception as e:
            self.update_info(f"Error resetting joints: {str(e)}")
            print(f"Reset Exception: {e}")

    # ...existing code...
    def move_to_reset(self):
        if not self.connection or not self.connection.is_connected:
            messagebox.showerror(
                "Robot Not Connected",
                "Cannot reset joints.\n\n"
                "Please connect to the robot first using the 'Connect' button."
            )
            return
        # Re-use reset_joints logic
        self.reset_joints()

    def move_to_position(self):
        if not self.connection or not self.connection.is_connected:
            messagebox.showerror(
                "Robot Not Connected",
                "Cannot move to position.\n\n"
                "Please connect to the robot first using the 'Connect' button."
            )
            return

        try:
            desc_pos = [
                self.constraint_frames['X'].get_value(),
                self.constraint_frames['Y'].get_value(),
                self.constraint_frames['Z'].get_value(),
                0.0, 0.0, 0.0
            ]

            self.update_info("Moving to position...")
            self.root.update()

            error = self.connection.move_l(desc_pos, self.velocity_var.get(), self.overdrive_var.get())

            if error == 0:
                self.current_pos['X'] = desc_pos[0]
                self.current_pos['Y'] = desc_pos[1]
                self.current_pos['Z'] = desc_pos[2]
                self.update_info("Movement completed successfully")
            else:
                messagebox.showerror(
                    "Movement Error",
                    f"Failed to move robot to position.\n\n"
                    f"Error Code: {error}\n\n"
                    f"Target Position:\n"
                    f"X: {desc_pos[0]:.2f}mm, Y: {desc_pos[1]:.2f}mm, Z: {desc_pos[2]:.2f}mm\n\n"
                    f"Please check if position is within safe range."
                )
                self.update_info(f"Movement failed with error {error}")
        except Exception as e:
            messagebox.showerror(
                "Movement Exception",
                f"An unexpected error occurred during movement:\n\n{str(e)}\n\n"
                f"Please try again or restart the connection."
            )
            self.update_info(f"Error: {str(e)}")

    def move_to_home(self):
        if not self.connection or not self.connection.is_connected:
            messagebox.showerror(
                "Robot Not Connected",
                "Cannot move to home position.\n\n"
                "Please connect to the robot first using the 'Connect' button."
            )
            return

        try:
            self.update_info("Moving to home position...")
            self.root.update()

            error = self.connection.move_l(HOME_POSITION, self.velocity_var.get(), self.overdrive_var.get())

            if error == 0:
                import time
                time.sleep(0.5)

                self.constraint_frames['X'].set_value(HOME_POSITION[0])
                self.constraint_frames['Y'].set_value(HOME_POSITION[1])
                self.constraint_frames['Z'].set_value(HOME_POSITION[2])

                self.current_pos['X'] = 0.0
                self.current_pos['Y'] = 0.0
                self.current_pos['Z'] = 100.0

                self.root.after(0, lambda: self.pos_label.config(text=f"X: 0.00  Y: 0.00  Z: 100.00"))
                self.update_info("Home position reached")
            else:
                messagebox.showerror(
                    "Home Position Error",
                    f"Failed to move robot to home position.\n\n"
                    f"Error Code: {error}\n\n"
                    f"Home Position: X: 0.0mm, Y: 0.0mm, Z: 100.0mm\n\n"
                    f"Please check robot status and try again."
                )
                self.update_info(f"Home movement failed with error {error}")
        except Exception as e:
            messagebox.showerror(
                "Home Movement Exception",
                f"An unexpected error occurred moving to home:\n\n{str(e)}\n\n"
                f"Please verify the robot is in a safe state."
            )
            self.update_info(f"Error: {str(e)}")



    def stop_motion(self):
        if not self.connection or not self.connection.is_connected:
            messagebox.showerror(
                "Robot Not Connected",
                "Cannot stop motion.\n\n"
                "Please connect to the robot first using the 'Connect' button."
            )
            return

        try:
            self.update_info("Stopping motion...")
            self.root.update()

            error = self.connection.stop_motion()

            if error == 0:
                self.update_info("Motion stopped")
            else:
                messagebox.showerror(
                    "Stop Motion Error",
                    f"Failed to stop robot motion.\n\n"
                    f"Error Code: {error}\n\n"
                    f"Please check robot status and try again."
                )
                self.update_info(f"Stop failed with error {error}")
        except Exception as e:
            messagebox.showerror(
                "Stop Motion Exception",
                f"An unexpected error occurred while stopping:\n\n{str(e)}\n\n"
                f"Please verify the robot is powered and connected."
            )
            self.update_info(f"Error: {str(e)}")

    def _update_vel_label(self, *args):
        self.vel_label.config(text=f"{self.velocity_var.get()}%")

    def _update_ovl_label(self, *args):
        self.ovl_label.config(text=f"{self.overdrive_var.get()}%")

    def update_info(self, message):
        self.info_label.config(text=message)

