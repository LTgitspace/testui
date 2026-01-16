import tkinter as tk
from tkinter import ttk, messagebox


class ConstraintFrame:
    def __init__(self, parent, axis, constraints, on_change_callback):
        self.axis = axis
        self.constraints = constraints
        self.on_change_callback = on_change_callback
        self.frame = ttk.Frame(parent)
        self.value_label = None
        self.slider = None
        self._create_widgets()

    def _create_widgets(self):
        ttk.Label(self.frame, text=f"{self.axis}-Axis:", font=("Arial", 10, "bold"), width=8).pack(side=tk.LEFT, padx=5)

        ttk.Label(self.frame, text="Min:").pack(side=tk.LEFT, padx=2)
        self.min_var = tk.StringVar(value=str(self.constraints[self.axis]['min']))
        self.min_entry = ttk.Entry(self.frame, textvariable=self.min_var, width=6)
        self.min_entry.pack(side=tk.LEFT, padx=2)
        self.min_var.trace_add('write', self._on_constraint_change)

        self.slider = ttk.Scale(
            self.frame,
            from_=self.constraints[self.axis]['min'],
            to=self.constraints[self.axis]['max'],
            orient=tk.HORIZONTAL
        )
        self.slider.set(self.constraints[self.axis]['current'])
        self.slider.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)

        ttk.Label(self.frame, text="Max:").pack(side=tk.LEFT, padx=2)
        self.max_var = tk.StringVar(value=str(self.constraints[self.axis]['max']))
        self.max_entry = ttk.Entry(self.frame, textvariable=self.max_var, width=6)
        self.max_entry.pack(side=tk.LEFT, padx=2)
        self.max_var.trace_add('write', self._on_constraint_change)

        self.value_label = ttk.Label(self.frame, text="0.00", font=("Arial", 10, "bold"), width=7)
        self.value_label.pack(side=tk.LEFT, padx=10)

        ttk.Label(self.frame, text="mm").pack(side=tk.LEFT, padx=5)

        self.slider.config(command=lambda val: self._on_slider_change(float(val)))

    def _on_constraint_change(self, *args):
        try:
            min_val = float(self.min_var.get())
            max_val = float(self.max_var.get())

            self.constraints[self.axis]['min'] = min_val
            self.constraints[self.axis]['max'] = max_val

            current = self.slider.get()
            self.slider.config(from_=min_val, to=max_val)

            clamped = max(min_val, min(max_val, current))
            self.slider.set(clamped)

            self.on_change_callback(f"{self.axis}-Axis constraint updated")
        except ValueError:
            messagebox.showerror(
                "Invalid Input",
                f"Please enter valid numbers for {self.axis}-Axis constraints.\n\n"
                f"Example: Min: -200, Max: 200\n"
                f"Current values have been restored."
            )
            self.min_var.set(str(self.constraints[self.axis]['min']))
            self.max_var.set(str(self.constraints[self.axis]['max']))

    def _on_slider_change(self, value):
        self.constraints[self.axis]['current'] = round(value, 2)
        self.value_label.config(text=f"{value:.2f}")

    def get_frame(self):
        return self.frame

    def get_value(self):
        return round(self.slider.get(), 2)

    def set_value(self, value):
        self.slider.set(value)

