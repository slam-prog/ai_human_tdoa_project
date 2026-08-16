from __future__ import annotations

from dataclasses import dataclass
import numpy as np

from .array_geometry import ArrayGeometry, validate_geometry


@dataclass(frozen=True)
class LocalizationResult3D:
    estimated_position: np.ndarray
    residual_vector: np.ndarray
    residual_norm: float
    iterations: int
    converged: bool


def _residuals(
    position: np.ndarray,
    microphone_positions: np.ndarray,
    measured_tdoa: np.ndarray,
    speed_of_sound: float,
    reference_index: int = 0,
) -> np.ndarray:
    ref = microphone_positions[reference_index]
    ref_distance = np.linalg.norm(position - ref)

    result = []
    for idx in range(len(microphone_positions)):
        if idx == reference_index:
            continue
        di = np.linalg.norm(position - microphone_positions[idx])
        model = (di - ref_distance) / speed_of_sound
        result.append(model - measured_tdoa[len(result)])

    return np.asarray(result, dtype=np.float64)


def _jacobian(
    position: np.ndarray,
    microphone_positions: np.ndarray,
    speed_of_sound: float,
    reference_index: int = 0,
) -> np.ndarray:
    ref = microphone_positions[reference_index]
    ref_vector = position - ref
    ref_distance = np.linalg.norm(ref_vector)
    ref_distance = max(ref_distance, 1e-12)

    rows = []
    for idx in range(len(microphone_positions)):
        if idx == reference_index:
            continue

        vec_i = position - microphone_positions[idx]
        dist_i = np.linalg.norm(vec_i)
        dist_i = max(dist_i, 1e-12)

        grad = (vec_i / dist_i - ref_vector / ref_distance) / speed_of_sound
        rows.append(grad)

    return np.asarray(rows, dtype=np.float64)


def initial_guess_from_array_center(
    geometry: ArrayGeometry,
) -> np.ndarray:
    validate_geometry(geometry)
    center = np.mean(geometry.microphone_positions, axis=0)
    return center + np.array([0.02, 0.02, 0.02], dtype=np.float64)


def solve_3d_source_position(
    geometry: ArrayGeometry,
    measured_tdoa_seconds: np.ndarray,
    reference_index: int = 0,
    initial_guess: np.ndarray | None = None,
    max_iterations: int = 100,
    tolerance: float = 1e-10,
    damping: float = 1e-6,
) -> LocalizationResult3D:
    validate_geometry(geometry)

    measured = np.asarray(measured_tdoa_seconds, dtype=np.float64)
    if measured.shape != (3,):
        raise ValueError("measured_tdoa_seconds يجب أن تكون بشكل (3,)")

    if initial_guess is None:
        current = initial_guess_from_array_center(geometry)
    else:
        current = np.asarray(initial_guess, dtype=np.float64)
        if current.shape != (3,):
            raise ValueError("initial_guess يجب أن تكون بشكل (3,)")

    mic = np.asarray(geometry.microphone_positions, dtype=np.float64)
    c = float(geometry.speed_of_sound)

    converged = False
    iterations = 0

    for iteration in range(1, max_iterations + 1):
        r = _residuals(
            position=current,
            microphone_positions=mic,
            measured_tdoa=measured,
            speed_of_sound=c,
            reference_index=reference_index,
        )

        j = _jacobian(
            position=current,
            microphone_positions=mic,
            speed_of_sound=c,
            reference_index=reference_index,
        )

        h = j.T @ j + damping * np.eye(3, dtype=np.float64)
        g = j.T @ r

        try:
            delta = np.linalg.solve(h, g)
        except np.linalg.LinAlgError:
            break

        updated = current - delta
        iterations = iteration

        if np.linalg.norm(delta) < tolerance:
            current = updated
            converged = True
            break

        current = updated

    final_residuals = _residuals(
        position=current,
        microphone_positions=mic,
        measured_tdoa=measured,
        speed_of_sound=c,
        reference_index=reference_index,
    )

    return LocalizationResult3D(
        estimated_position=current,
        residual_vector=final_residuals,
        residual_norm=float(np.linalg.norm(final_residuals)),
        iterations=iterations,
        converged=converged,
    )


def position_error_millimeters(
    true_position: np.ndarray,
    estimated_position: np.ndarray,
) -> float:
    true_position = np.asarray(true_position, dtype=np.float64)
    estimated_position = np.asarray(estimated_position, dtype=np.float64)
    return float(np.linalg.norm(estimated_position - true_position) * 1000.0)
