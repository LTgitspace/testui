import tkinter as tk
from tkinter import ttk, messagebox
import tkinter as tk
from src.config import *
from src.constraint_frame import ConstraintFrame
from src.config import HOME_POSITION, ROTATION_CONSTRAINTS


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
        self.rotation_constraints = {k: v.copy() for k, v in ROTATION_CONSTRAINTS.items()}
        self.current_pos = DEFAULT_POSITION.copy()
        self.current_rot = DEFAULT_ROTATION.copy()

        self.constraint_frames = {}
        self.rotation_frames = {}
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

        self.jog_velocity_var = tk.IntVar(value=DEFAULT_VELOCITY)
        self.jog_overdrive_var = tk.IntVar(value=DEFAULT_OVERDRIVE)
        self.jog_axis_var = tk.StringVar(value="X")
        self.jogging_active = False
        self.jog_vel_label = None
        self.jog_ovl_label = None
        self.jog_positive_btn = None
        self.jog_negative_btn = None
        self.jog_stop_btn = None

        self.create_widgets()

    def create_widgets(self):
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        self._create_connection_frame(main_frame)
        self._create_control_frame(main_frame)
        self._create_movement_frame(main_frame)
        self._create_jogging_frame(main_frame)
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
        control_frame = ttk.LabelFrame(parent, text="Position & Rotation Control", padding="15")
        control_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)

        ttk.Label(control_frame, text="Position (mm):", font=("Arial", 10, "bold")).grid(row=0, column=0, columnspan=3, sticky=tk.W, padx=5, pady=5)

        for idx, axis in enumerate(['X', 'Y', 'Z']):
            constraint_frame = ConstraintFrame(
                control_frame,
                axis,
                self.axis_constraints,
                self.update_info
            )
            constraint_frame.get_frame().grid(row=idx+1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=8)
            self.constraint_frames[axis] = constraint_frame

        ttk.Label(control_frame, text="Rotation (degrees):", font=("Arial", 10, "bold")).grid(row=4, column=0, columnspan=3, sticky=tk.W, padx=5, pady=5)

        for idx, axis in enumerate(['Rx', 'Ry', 'Rz']):
            constraint_frame = ConstraintFrame(
                control_frame,
                axis,
                self.rotation_constraints,
                self.update_info
            )
            constraint_frame.get_frame().grid(row=idx+5, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=8)
            self.rotation_frames[axis] = constraint_frame

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

        self.reset_btn = ttk.Button(btn_frame, text="Reset Joints", command=self.move_to_reset, state=tk.DISABLED)
        self.reset_btn.pack(side=tk.LEFT, padx=5)

        move_frame.columnconfigure(1, weight=1)

    def _create_jogging_frame(self, parent):
        jog_frame = ttk.LabelFrame(parent, text="Jogging Control", padding="10")
        jog_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)

        ttk.Label(jog_frame, text="Jog Axis:").grid(row=0, column=0, padx=5)
        axis_combo = ttk.Combobox(
            jog_frame,
            textvariable=self.jog_axis_var,
            values=['X', 'Y', 'Z', 'Rx', 'Ry', 'Rz'],
            state='readonly',
            width=5
        )
        axis_combo.grid(row=0, column=1, padx=5)

        ttk.Label(jog_frame, text="Jog Velocity (%):").grid(row=1, column=0, padx=5)
        jog_vel_scale = ttk.Scale(jog_frame, from_=MIN_VELOCITY, to=MAX_VELOCITY, variable=self.jog_velocity_var, orient=tk.HORIZONTAL)
        jog_vel_scale.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=5)
        self.jog_vel_label = ttk.Label(jog_frame, text=f"{DEFAULT_VELOCITY}%", width=4)
        self.jog_vel_label.grid(row=1, column=2, padx=5)
        self.jog_velocity_var.trace_add('write', self._update_jog_vel_label)

        ttk.Label(jog_frame, text="Jog Overdrive (%):").grid(row=2, column=0, padx=5)
        jog_ovl_scale = ttk.Scale(jog_frame, from_=MIN_OVERDRIVE, to=MAX_OVERDRIVE, variable=self.jog_overdrive_var, orient=tk.HORIZONTAL)
        jog_ovl_scale.grid(row=2, column=1, sticky=(tk.W, tk.E), padx=5)
        self.jog_ovl_label = ttk.Label(jog_frame, text=f"{DEFAULT_OVERDRIVE}%", width=4)
        self.jog_ovl_label.grid(row=2, column=2, padx=5)
        self.jog_overdrive_var.trace_add('write', self._update_jog_ovl_label)

        jog_btn_frame = ttk.Frame(jog_frame)
        jog_btn_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)

        self.jog_positive_btn = ttk.Button(jog_btn_frame, text="Jog +", command=self.start_jog_positive, state=tk.DISABLED)
        self.jog_positive_btn.pack(side=tk.LEFT, padx=5)

        self.jog_negative_btn = ttk.Button(jog_btn_frame, text="Jog -", command=self.start_jog_negative, state=tk.DISABLED)
        self.jog_negative_btn.pack(side=tk.LEFT, padx=5)

        self.jog_stop_btn = ttk.Button(jog_btn_frame, text="Stop Jog", command=self.stop_jog, state=tk.DISABLED)
        self.jog_stop_btn.pack(side=tk.LEFT, padx=5)

        jog_frame.columnconfigure(1, weight=1)

    def _create_status_frame(self, parent):
        status_frame = ttk.LabelFrame(parent, text="Robot Status", padding="10")
        status_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)

        ttk.Label(status_frame, text="Current Position (mm):").grid(row=0, column=0, sticky=tk.W, padx=5)
        self.pos_label = ttk.Label(status_frame, text=f"X: {DEFAULT_POSITION['X']:.2f}  Y: {DEFAULT_POSITION['Y']:.2f}  Z: {DEFAULT_POSITION['Z']:.2f}  Rx: {DEFAULT_ROTATION['Rx']:.2f}°  Ry: {DEFAULT_ROTATION['Ry']:.2f}°  Rz: {DEFAULT_ROTATION['Rz']:.2f}°", font=("Arial", 11, "bold"))
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
                self.jog_positive_btn.config(state=tk.NORMAL)
                self.jog_negative_btn.config(state=tk.NORMAL)
                self.jog_stop_btn.config(state=tk.NORMAL)

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
        self.jog_positive_btn.config(state=tk.DISABLED)
        self.jog_negative_btn.config(state=tk.DISABLED)
        self.jog_stop_btn.config(state=tk.DISABLED)

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

                    if state_pkg.tl_cur_pos:
                        x = state_pkg.tl_cur_pos[0]
                        y = state_pkg.tl_cur_pos[1]
                        z = state_pkg.tl_cur_pos[2]
                        rx = state_pkg.tl_cur_pos[3]
                        ry = state_pkg.tl_cur_pos[4]
                        rz = state_pkg.tl_cur_pos[5]

                        self.current_pos['X'] = x
                        self.current_pos['Y'] = y
                        self.current_pos['Z'] = z
                        self.current_rot['Rx'] = rx
                        self.current_rot['Ry'] = ry
                        self.current_rot['Rz'] = rz

                        def update_sliders():
                            self.constraint_frames['X'].set_value(x)
                            self.constraint_frames['Y'].set_value(y)
                            self.constraint_frames['Z'].set_value(z)
                            self.rotation_frames['Rx'].set_value(rx)
                            self.rotation_frames['Ry'].set_value(ry)
                            self.rotation_frames['Rz'].set_value(rz)

                            self.pos_label.config(
                                text=f"X: {x:.2f}  Y: {y:.2f}  Z: {z:.2f}  Rx: {rx:.2f}°  Ry: {ry:.2f}°  Rz: {rz:.2f}°"
                            )

                        self.root.after(0, update_sliders)

                time.sleep(MONITOR_THREAD_INTERVAL)
            except Exception as e:
                pass

    def reset_joints(self):
        if not self.connection or not self.connection.is_connected:
            return

        import threading
        thread = threading.Thread(target=self._reset_joints_thread, daemon=True)
        thread.start()

    def _reset_joints_thread(self):
        try:
            self.root.after(0, lambda: self.update_info("Resetting joints to 0 position..."))

            error = self.connection.move_j(RESET_JOINTS_POSITION, RESET_VELOCITY, RESET_OVERDRIVE)

            if error == 0:
                import time
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
                self.root.after(0, lambda: self.update_info("Reset Complete: Joints at 0 degrees"))
            else:
                self.root.after(0, lambda err=error: self.update_info(f"Joint reset failed with error {err}"))
        except Exception as e:
            self.root.after(0, lambda ex=str(e): self.update_info(f"Error resetting joints: {ex}"))
            print(f"Reset Exception: {e}")

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

        import threading
        thread = threading.Thread(target=self._move_to_position_thread, daemon=True)
        thread.start()

    def _move_to_position_thread(self):
        try:
            x = self.constraint_frames['X'].get_value()
            y = self.constraint_frames['Y'].get_value()
            z = self.constraint_frames['Z'].get_value()
            rx = self.rotation_frames['Rx'].get_value()
            ry = self.rotation_frames['Ry'].get_value()
            rz = self.rotation_frames['Rz'].get_value()

            desc_pos = [x, y, z, rx, ry, rz]

            self.root.after(0, lambda: self.update_info("Moving to position..."))

            error = self.connection.move_l(desc_pos, self.velocity_var.get(), self.overdrive_var.get())

            if error == 0:
                self.current_pos['X'] = desc_pos[0]
                self.current_pos['Y'] = desc_pos[1]
                self.current_pos['Z'] = desc_pos[2]
                self.current_rot['Rx'] = desc_pos[3]
                self.current_rot['Ry'] = desc_pos[4]
                self.current_rot['Rz'] = desc_pos[5]
                self.root.after(0, lambda pos=desc_pos: self.pos_label.config(
                    text=f"X: {pos[0]:.2f}  Y: {pos[1]:.2f}  Z: {pos[2]:.2f}  Rx: {pos[3]:.2f}°  Ry: {pos[4]:.2f}°  Rz: {pos[5]:.2f}°"
                ))
                self.root.after(0, lambda: self.update_info("Movement completed successfully"))
            else:
                self.root.after(0, lambda err=error, pos=desc_pos: messagebox.showerror(
                    "Movement Error",
                    f"Failed to move robot to position.\n\n"
                    f"Error Code: {err}\n\n"
                    f"Target Position:\n"
                    f"X: {pos[0]:.2f}mm, Y: {pos[1]:.2f}mm, Z: {pos[2]:.2f}mm\n"
                    f"Rx: {pos[3]:.2f}°, Ry: {pos[4]:.2f}°, Rz: {pos[5]:.2f}°\n\n"
                    f"Please check if position is within safe range."
                ))
                self.root.after(0, lambda err=error: self.update_info(f"Movement failed with error {err}"))
        except Exception as e:
            self.root.after(0, lambda ex=str(e): messagebox.showerror(
                "Movement Exception",
                f"An unexpected error occurred during movement:\n\n{ex}\n\n"
                f"Please try again or restart the connection."
            ))
            self.root.after(0, lambda ex=str(e): self.update_info(f"Error: {ex}"))

    def move_to_home(self):
        if not self.connection or not self.connection.is_connected:
            messagebox.showerror(
                "Robot Not Connected",
                "Cannot move to home position.\n\n"
                "Please connect to the robot first using the 'Connect' button."
            )
            return

        import threading
        thread = threading.Thread(target=self._move_to_home_thread, daemon=True)
        thread.start()

    def _move_to_home_thread(self):
        try:
            self.root.after(0, lambda: self.update_info("Moving to home position..."))

            error = self.connection.move_l(HOME_POSITION, self.velocity_var.get(), self.overdrive_var.get())

            if error == 0:
                import time
                time.sleep(0.5)

                self.constraint_frames['X'].set_value(HOME_POSITION[0])
                self.constraint_frames['Y'].set_value(HOME_POSITION[1])
                self.constraint_frames['Z'].set_value(HOME_POSITION[2])
                self.rotation_frames['Rx'].set_value(HOME_POSITION[3])
                self.rotation_frames['Ry'].set_value(HOME_POSITION[4])
                self.rotation_frames['Rz'].set_value(HOME_POSITION[5])

                self.current_pos['X'] = HOME_POSITION[0]
                self.current_pos['Y'] = HOME_POSITION[1]
                self.current_pos['Z'] = HOME_POSITION[2]
                self.current_rot['Rx'] = HOME_POSITION[3]
                self.current_rot['Ry'] = HOME_POSITION[4]
                self.current_rot['Rz'] = HOME_POSITION[5]

                self.root.after(0, lambda: self.pos_label.config(
                    text=f"X: {HOME_POSITION[0]:.2f}  Y: {HOME_POSITION[1]:.2f}  Z: {HOME_POSITION[2]:.2f}  Rx: {HOME_POSITION[3]:.2f}°  Ry: {HOME_POSITION[4]:.2f}°  Rz: {HOME_POSITION[5]:.2f}°"
                ))
                self.root.after(0, lambda: self.update_info("Home position reached"))
            else:
                self.root.after(0, lambda err=error: messagebox.showerror(
                    "Home Position Error",
                    f"Failed to move robot to home position.\n\n"
                    f"Error Code: {err}\n\n"
                    f"Home Position: X: {HOME_POSITION[0]:.1f}mm, Y: {HOME_POSITION[1]:.1f}mm, Z: {HOME_POSITION[2]:.1f}mm\n\n"
                    f"Please check robot status and try again."
                ))
                self.root.after(0, lambda err=error: self.update_info(f"Home position move failed with error {err}"))
        except Exception as e:
            self.root.after(0, lambda ex=str(e): messagebox.showerror(
                "Home Position Exception",
                f"An unexpected error occurred moving to home:\n\n{ex}"
            ))
            self.root.after(0, lambda ex=str(e): self.update_info(f"Error: {ex}"))

    def stop_motion(self):
        if not self.connection or not self.connection.is_connected:
            messagebox.showerror(
                "Robot Not Connected",
                "Cannot stop motion.\n\n"
                "Please connect to the robot first using the 'Connect' button."
            )
            return

        import threading
        thread = threading.Thread(target=self._stop_motion_thread, daemon=True)
        thread.start()

    def _stop_motion_thread(self):
        try:
            self.root.after(0, lambda: self.update_info("Stopping motion..."))

            error = self.connection.stop_motion()

            if error == 0:
                self.root.after(0, lambda: self.update_info("Motion stopped"))
            else:
                self.root.after(0, lambda err=error: messagebox.showerror(
                    "Stop Motion Error",
                    f"Failed to stop robot motion.\n\n"
                    f"Error Code: {err}\n\n"
                    f"Please check robot status and try again."
                ))
                self.root.after(0, lambda err=error: self.update_info(f"Stop failed with error {err}"))
        except Exception as e:
            self.root.after(0, lambda ex=str(e): messagebox.showerror(
                "Stop Motion Exception",
                f"An unexpected error occurred while stopping:\n\n{ex}\n\n"
                f"Please verify the robot is powered and connected."
            ))
            self.root.after(0, lambda ex=str(e): self.update_info(f"Error: {ex}"))

    def _update_vel_label(self, *args):
        self.vel_label.config(text=f"{self.velocity_var.get()}%")

    def _update_ovl_label(self, *args):
        self.ovl_label.config(text=f"{self.overdrive_var.get()}%")

    def _update_jog_vel_label(self, *args):
        self.jog_vel_label.config(text=f"{self.jog_velocity_var.get()}%")

    def _update_jog_ovl_label(self, *args):
        self.jog_ovl_label.config(text=f"{self.jog_overdrive_var.get()}%")

    def start_jog_positive(self):
        if not self.connection or not self.connection.is_connected:
            messagebox.showerror(
                "Robot Not Connected",
                "Cannot jog robot.\n\n"
                "Please connect to the robot first using the 'Connect' button."
            )
            return

        import threading
        thread = threading.Thread(target=self._start_jog_positive_thread, daemon=True)
        thread.start()

    def _start_jog_positive_thread(self):
        try:
            axis = self.jog_axis_var.get()
            joint_map = {'X': 1, 'Y': 2, 'Z': 3, 'Rx': 4, 'Ry': 5, 'Rz': 6}
            joint_nb = joint_map.get(axis, 1)

            # FIX: Use ref=2 (Base Coordinate) for X,Y,Z. ref=0 is for Joints (J1-J6).
            ref = 2

            self.root.after(0, lambda: self.update_info(f"Jogging {axis} in positive direction..."))

            # FIX: Use keyword arguments to ensure values go to the right place
            error = self.connection.start_jog(
                ref=ref,
                nb=joint_nb,
                direction=1,      # 1 = Positive
                vel=self.jog_velocity_var.get(),
                acc=100.0,
                max_dis=200.0     # Increased safety distance slightly
            )

            if error == 0:
                self.jogging_active = True
                self.root.after(0, lambda: self.update_info(f"Jogging {axis} positive"))
            else:
                self.root.after(0, lambda err=error, ax=axis: messagebox.showerror(
                    "Jog Error",
                    f"Failed to start jog.\nError: {err}\nCheck if 'ref=2' is supported."
                ))
        except Exception as e:
            self.root.after(0, lambda ex=str(e): self.update_info(f"Error: {ex}"))

    def start_jog_negative(self):
        if not self.connection or not self.connection.is_connected:
            messagebox.showerror(
                "Robot Not Connected",
                "Cannot jog robot.\n\n"
                "Please connect to the robot first using the 'Connect' button."
            )
            return

        import threading
        thread = threading.Thread(target=self._start_jog_negative_thread, daemon=True)
        thread.start()

    def _start_jog_negative_thread(self):
        try:
            axis = self.jog_axis_var.get()
            joint_map = {'X': 1, 'Y': 2, 'Z': 3, 'Rx': 4, 'Ry': 5, 'Rz': 6}
            joint_nb = joint_map.get(axis, 1)

            # FIX: Use ref=2 for Base Coordinate
            ref = 2

            self.root.after(0, lambda: self.update_info(f"Jogging {axis} in negative direction..."))

            # FIX: Explicitly send 0 for Negative (not -1)
            error = self.connection.start_jog(
                ref=ref,
                nb=joint_nb,
                direction=0,       # 0 = Negative (CRITICAL FIX)
                vel=self.jog_velocity_var.get(),
                acc=100.0,
                max_dis=200.0
            )

            if error == 0:
                self.jogging_active = True
                self.root.after(0, lambda: self.update_info(f"Jogging {axis} negative"))
            else:
                self.root.after(0, lambda err=error, ax=axis: messagebox.showerror(
                    "Jog Error",
                    f"Failed to start jog.\nError: {err}"
                ))
        except Exception as e:
            self.root.after(0, lambda ex=str(e): self.update_info(f"Error: {ex}"))

    def stop_jog(self):
        if not self.connection or not self.connection.is_connected:
            messagebox.showerror(
                "Robot Not Connected",
                "Cannot stop jog.\n\n"
                "Please connect to the robot first using the 'Connect' button."
            )
            return

        import threading
        thread = threading.Thread(target=self._stop_jog_thread, daemon=True)
        thread.start()

    def _stop_jog_thread(self):
        try:
            self.root.after(0, lambda: self.update_info("Stopping jog..."))

            error = self.connection.stop_jog(ref=1)

            if error == 0:
                self.jogging_active = False
                self.root.after(0, lambda: self.update_info("Jog stopped"))
            else:
                self.root.after(0, lambda err=error: messagebox.showerror(
                    "Stop Jog Error",
                    f"Failed to stop jog.\n\n"
                    f"Error Code: {err}"
                ))
                self.root.after(0, lambda err=error: self.update_info(f"Stop jog failed with error {err}"))
        except Exception as e:
            self.root.after(0, lambda ex=str(e): messagebox.showerror(
                "Stop Jog Exception",
                f"An unexpected error occurred while stopping jog:\n\n{ex}"
            ))
            self.root.after(0, lambda ex=str(e): self.update_info(f"Error: {ex}"))

    def update_info(self, message):
        self.info_label.config(text=message)

