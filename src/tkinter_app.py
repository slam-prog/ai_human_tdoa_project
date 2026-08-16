from __future__ import annotations

import tkinter as tk
from tkinter import ttk, messagebox

import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from .array_geometry import ArrayGeometry
from .analog_simulation_3d import (
    AnalogSimulation3DConfig,
    run_simulation_3d,
)
from .metrics_3d import calculate_metrics_3d, metrics_text


class TDOA3DApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()

        self.title("4-Microphone 3D TDOA Analog Simulation")
        self.geometry("1400x900")
        self.minsize(1200, 760)

        self._build_variables()
        self._build_layout()
        self._build_plots()

    def _build_variables(self) -> None:
        default_mics = [
            (0.00, 0.00, 0.00),
            (0.10, 0.00, 0.00),
            (0.00, 0.10, 0.00),
            (0.00, 0.00, 0.10),
        ]
        default_src = (0.06, 0.05, 0.07)

        self.mic_vars: list[list[tk.StringVar]] = []
        for xyz in default_mics:
            row = [tk.StringVar(value=f"{v:.4f}") for v in xyz]
            self.mic_vars.append(row)

        self.src_vars = [tk.StringVar(value=f"{v:.4f}") for v in default_src]

        self.speed_var = tk.StringVar(value="343.0")
        self.noise_var = tk.StringVar(value="0.02")
        self.gain1_var = tk.StringVar(value="1.00")
        self.gain2_var = tk.StringVar(value="0.98")
        self.gain3_var = tk.StringVar(value="1.02")
        self.gain4_var = tk.StringVar(value="0.96")
        self.search_min_var = tk.StringVar(value="0.0")
        self.search_max_var = tk.StringVar(value="60.0")
        self.search_points_var = tk.StringVar(value="801")
        self.numerical_points_var = tk.StringVar(value="40000")
        self.fit_gain_var = tk.BooleanVar(value=True)
        self.refine_var = tk.BooleanVar(value=True)

    def _build_layout(self) -> None:
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)

        control_frame = ttk.Frame(self, padding=10)
        control_frame.grid(row=0, column=0, sticky="nsw")
        plot_frame = ttk.Frame(self, padding=10)
        plot_frame.grid(row=0, column=1, sticky="nsew")

        plot_frame.columnconfigure(0, weight=1)
        plot_frame.rowconfigure(0, weight=1)
        plot_frame.rowconfigure(1, weight=1)

        ttk.Label(control_frame, text="Microphones (m)", font=("Segoe UI", 10, "bold")).grid(
            row=0, column=0, columnspan=4, sticky="w", pady=(0, 6)
        )

        for i in range(4):
            ttk.Label(control_frame, text=f"Mic {i+1}").grid(row=1 + i, column=0, sticky="w")
            for j, axis in enumerate(("x", "y", "z")):
                ttk.Entry(control_frame, textvariable=self.mic_vars[i][j], width=8).grid(
                    row=1 + i, column=1 + j, padx=2, pady=2
                )

        base_row = 6
        ttk.Label(control_frame, text="Source (m)", font=("Segoe UI", 10, "bold")).grid(
            row=base_row, column=0, columnspan=4, sticky="w", pady=(12, 6)
        )

        for j in range(3):
            ttk.Entry(control_frame, textvariable=self.src_vars[j], width=8).grid(
                row=base_row + 1, column=1 + j, padx=2, pady=2
            )

        param_row = base_row + 3
        fields = [
            ("Speed of sound", self.speed_var),
            ("Noise std", self.noise_var),
            ("Gain ch1", self.gain1_var),
            ("Gain ch2", self.gain2_var),
            ("Gain ch3", self.gain3_var),
            ("Gain ch4", self.gain4_var),
            ("Search min (us)", self.search_min_var),
            ("Search max (us)", self.search_max_var),
            ("Search points", self.search_points_var),
            ("Numerical points", self.numerical_points_var),
        ]

        ttk.Label(control_frame, text="Parameters", font=("Segoe UI", 10, "bold")).grid(
            row=param_row, column=0, columnspan=4, sticky="w", pady=(12, 6)
        )

        for idx, (label, var) in enumerate(fields, start=param_row + 1):
            ttk.Label(control_frame, text=label).grid(row=idx, column=0, sticky="w")
            ttk.Entry(control_frame, textvariable=var, width=12).grid(
                row=idx, column=1, columnspan=2, sticky="we", pady=2
            )

        ttk.Checkbutton(
            control_frame,
            text="Fit gain",
            variable=self.fit_gain_var,
        ).grid(row=param_row + len(fields) + 1, column=0, sticky="w", pady=(8, 2))

        ttk.Checkbutton(
            control_frame,
            text="Refine minimum",
            variable=self.refine_var,
        ).grid(row=param_row + len(fields) + 2, column=0, sticky="w", pady=2)

        ttk.Button(
            control_frame,
            text="Run Simulation",
            command=self.run_simulation,
        ).grid(row=param_row + len(fields) + 3, column=0, columnspan=3, sticky="we", pady=(12, 8))

        self.output_text = tk.Text(control_frame, width=42, height=22, wrap="word")
        self.output_text.grid(
            row=param_row + len(fields) + 4, column=0, columnspan=4, sticky="nsew", pady=(8, 0)
        )

    def _build_plots(self) -> None:
        self.figure = Figure(figsize=(10, 8), dpi=100)
        self.ax_3d = self.figure.add_subplot(211, projection="3d")
        self.ax_energy = self.figure.add_subplot(212)

        self.canvas = FigureCanvasTkAgg(self.figure, master=self)
        widget = self.canvas.get_tk_widget()
        widget.grid(row=0, column=1, sticky="nsew")

    def _read_geometry(self) -> ArrayGeometry:
        mic_positions = np.array(
            [[float(v.get()) for v in row] for row in self.mic_vars],
            dtype=np.float64,
        )
        source_position = np.array(
            [float(v.get()) for v in self.src_vars],
            dtype=np.float64,
        )
        speed = float(self.speed_var.get())

        return ArrayGeometry(
            microphone_positions=mic_positions,
            source_position=source_position,
            speed_of_sound=speed,
        )

    def _read_config(self) -> AnalogSimulation3DConfig:
        noise = float(self.noise_var.get())
        gains = (
            float(self.gain1_var.get()),
            float(self.gain2_var.get()),
            float(self.gain3_var.get()),
            float(self.gain4_var.get()),
        )

        return AnalogSimulation3DConfig(
            numerical_points=int(self.numerical_points_var.get()),
            min_search_delay_seconds=float(self.search_min_var.get()) * 1e-6,
            max_search_delay_seconds=float(self.search_max_var.get()) * 1e-6,
            search_points=int(self.search_points_var.get()),
            channel_gains=gains,
            channel_noise_stds=(noise, noise, noise, noise),
            fit_gain=bool(self.fit_gain_var.get()),
            refine_minimum=bool(self.refine_var.get()),
        )

    def run_simulation(self) -> None:
        try:
            geometry = self._read_geometry()
            config = self._read_config()
            result = run_simulation_3d(geometry=geometry, config=config)
            metrics = calculate_metrics_3d(result)

            self._update_text(result, metrics_text(metrics))
            self._update_plots(result)

        except Exception as exc:
            messagebox.showerror("Simulation Error", str(exc))

    def _update_text(self, result, metrics_report: str) -> None:
        est = result.localization_result.estimated_position
        true = result.geometry.source_position

        lines = [
            metrics_report,
            "",
            "True source position (m):",
            f"  x={true[0]:.6f}, y={true[1]:.6f}, z={true[2]:.6f}",
            "Estimated source position (m):",
            f"  x={est[0]:.6f}, y={est[1]:.6f}, z={est[2]:.6f}",
            "",
            "TDOA results against reference mic:",
        ]

        for idx, pair in enumerate(result.pair_results, start=1):
            lines.append(
                f"  Mic {pair.microphone_index + 1}: "
                f"true={pair.true_tdoa_seconds * 1e6:.6f} us, "
                f"estimated={pair.estimated_tdoa_seconds * 1e6:.6f} us"
            )

        self.output_text.delete("1.0", tk.END)
        self.output_text.insert(tk.END, "\n".join(lines))

    def _update_plots(self, result) -> None:
        self.ax_3d.clear()
        self.ax_energy.clear()

        mic = result.geometry.microphone_positions
        true_src = result.geometry.source_position
        est_src = result.localization_result.estimated_position

        self.ax_3d.scatter(mic[:, 0], mic[:, 1], mic[:, 2], s=80, label="Microphones")
        self.ax_3d.scatter(
            [true_src[0]], [true_src[1]], [true_src[2]],
            s=120, marker="^", label="True Source"
        )
        self.ax_3d.scatter(
            [est_src[0]], [est_src[1]], [est_src[2]],
            s=120, marker="x", label="Estimated Source"
        )

        for i in range(4):
            self.ax_3d.text(mic[i, 0], mic[i, 1], mic[i, 2], f"M{i+1}")

        self.ax_3d.set_title("3D Microphone Array and Source Position")
        self.ax_3d.set_xlabel("X (m)")
        self.ax_3d.set_ylabel("Y (m)")
        self.ax_3d.set_zlabel("Z (m)")
        self.ax_3d.legend()

        for pair in result.pair_results:
            delays_us = pair.search_result.delays_seconds * 1e6
            energies = pair.search_result.energies
            self.ax_energy.plot(
                delays_us,
                energies,
                label=f"Mic {pair.microphone_index + 1}"
            )

        self.ax_energy.set_title("Residual Energy vs Compensation Delay")
        self.ax_energy.set_xlabel("Compensation Delay (us)")
        self.ax_energy.set_ylabel("Residual Energy")
        self.ax_energy.grid(True, alpha=0.3)
        self.ax_energy.legend()

        self.figure.tight_layout()
        self.canvas.draw()


def main() -> None:
    app = TDOA3DApp()
    app.mainloop()


if __name__ == "__main__":
    main()
