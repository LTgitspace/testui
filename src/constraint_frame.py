import tkinter as tk
from tkinter import ttk

class ConstraintFrame:
    def __init__(self, parent, axis_name, constraints, info_callback):
        self.axis = axis_name
        self.constraints = constraints
        self.update_info = info_callback
        self.frame = ttk.Frame(parent)

        self.var = tk.DoubleVar(value=constraints[axis_name]['current'])

        # Label
        ttk.Label(self.frame, text=f"{self.axis}:", width=3, font=("Arial", 10, "bold")).pack(side=tk.LEFT, padx=5)

        # Value Label
        self.val_label = ttk.Label(self.frame, text=f"{self.var.get():.2f}", width=6)
        self.val_label.pack(side=tk.LEFT, padx=5)

        # Slider
        self.slider = ttk.Scale(
            self.frame,
            from_=constraints[axis_name]['min'],
            to=constraints[axis_name]['max'],
            orient=tk.HORIZONTAL,
            variable=self.var,
            length=200
        )
        self.slider.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)

        # Trace for updates
        self.slider.configure(command=self._on_slider_change)

        # Entry for manual input
        # self.entry = ttk.Entry(self.frame, textvariable=self.var, width=6)
        # self.entry.pack(side=tk.LEFT, padx=5)

    def get_frame(self):
        return self.frame

    def _on_slider_change(self, val):
        self.val_label.config(text=f"{float(val):.2f}")
        # Optionally callback to main

    def set_value(self, value):
        self.var.set(value)
        self.val_label.config(text=f"{value:.2f}")

    def get_value(self):
        return self.var.get()

