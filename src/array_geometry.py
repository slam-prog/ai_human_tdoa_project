from __future__ import annotations

from dataclasses import dataclass
import numpy as np


@dataclass(frozen=True)
class ArrayGeometry:
    microphone_positions: np.ndarray
    source_position: np.ndarray
    speed_of_sound: float = 343.0


def _as_float_array(value: np.ndarray | list[float]) -> np.ndarray:
    return np.asarray(value, dtype=np.float64)


def validate_geometry(geometry: ArrayGeometry) -> None:
    mic = _as_float_array(geometry.microphone_positions)
    src = _as_float_array(geometry.source_position)

    if mic.shape != (4, 3):
        raise ValueError("microphone_positions يجب أن تكون بشكل (4, 3)")

    if src.shape != (3,):
        raise ValueError("source_position يجب أن تكون بشكل (3,)")

    if not np.all(np.isfinite(mic)):
        raise ValueError("microphone_positions تحتوي على قيم غير صالحة")

    if not np.all(np.isfinite(src)):
        raise ValueError("source_position تحتوي على قيم غير صالحة")

    if geometry.speed_of_sound <= 0:
        raise ValueError("speed_of_sound يجب أن تكون أكبر من صفر")

    unique_rows = np.unique(mic, axis=0)
    if unique_rows.shape[0] != 4:
        raise ValueError("يجب أن تكون مواضع الميكروفونات الأربعة مختلفة")


def compute_distances(
    geometry: ArrayGeometry,
) -> np.ndarray:
    validate_geometry(geometry)
    return np.linalg.norm(
        geometry.microphone_positions - geometry.source_position,
        axis=1,
    )


def compute_arrival_times(
    geometry: ArrayGeometry,
) -> np.ndarray:
    distances = compute_distances(geometry)
    return distances / geometry.speed_of_sound


def compute_tdoa_against_reference(
    arrival_times: np.ndarray,
    reference_index: int = 0,
) -> np.ndarray:
    arrival_times = np.asarray(arrival_times, dtype=np.float64)

    if arrival_times.shape != (4,):
        raise ValueError("arrival_times يجب أن تكون بشكل (4,)")

    if reference_index < 0 or reference_index > 3:
        raise ValueError("reference_index خارج المجال")

    reference_time = arrival_times[reference_index]
    indices = [i for i in range(4) if i != reference_index]
    return arrival_times[indices] - reference_time
