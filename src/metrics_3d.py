from __future__ import annotations

from dataclasses import dataclass
import numpy as np

from .analog_simulation_3d import SimulationResult3D


@dataclass(frozen=True)
class MetricsSummary3D:
    mean_abs_tdoa_error_us: float
    max_abs_tdoa_error_us: float
    position_error_mm: float
    residual_norm: float
    converged: bool
    iterations: int


def calculate_metrics_3d(
    result: SimulationResult3D,
) -> MetricsSummary3D:
    tdoa_error_us = (
        (result.estimated_tdoa_seconds - result.true_tdoa_seconds) * 1e6
    )

    return MetricsSummary3D(
        mean_abs_tdoa_error_us=float(np.mean(np.abs(tdoa_error_us))),
        max_abs_tdoa_error_us=float(np.max(np.abs(tdoa_error_us))),
        position_error_mm=float(result.position_error_mm),
        residual_norm=float(result.localization_result.residual_norm),
        converged=bool(result.localization_result.converged),
        iterations=int(result.localization_result.iterations),
    )


def metrics_text(
    metrics: MetricsSummary3D,
) -> str:
    lines = [
        "3D Localization Metrics",
        "=" * 36,
        f"Mean |TDOA error|: {metrics.mean_abs_tdoa_error_us:.6f} us",
        f"Max |TDOA error| : {metrics.max_abs_tdoa_error_us:.6f} us",
        f"Position error   : {metrics.position_error_mm:.6f} mm",
        f"Residual norm    : {metrics.residual_norm:.6e}",
        f"Converged        : {metrics.converged}",
        f"Iterations       : {metrics.iterations}",
    ]
    return "\n".join(lines)
