from __future__ import annotations

from dataclasses import dataclass
import numpy as np

from .analog_channel_model import AnalogChannelConfig, apply_analog_channel
from .analog_signal_model import (
    DEFAULT_SIGNAL_CONFIG,
    SignalConfig,
    create_time_axis,
    generate_continuous_signal,
)
from .array_geometry import (
    ArrayGeometry,
    compute_arrival_times,
    compute_tdoa_against_reference,
    validate_geometry,
)
from .localization_3d import (
    LocalizationResult3D,
    solve_3d_source_position,
    position_error_millimeters,
)
from .residual_energy import (
    ResidualSearchResult,
    search_minimum_residual,
)


@dataclass(frozen=True)
class AnalogSimulation3DConfig:
    duration_seconds: float = DEFAULT_SIGNAL_CONFIG.duration
    numerical_points: int = 40_000

    min_search_delay_seconds: float = 0.0
    max_search_delay_seconds: float = 60.0e-6
    search_points: int = 801

    channel_gains: tuple[float, float, float, float] = (1.0, 0.98, 1.02, 0.96)
    channel_noise_stds: tuple[float, float, float, float] = (0.02, 0.02, 0.02, 0.02)
    lowpass_cutoff_hz: float | None = None

    fit_gain: bool = True
    refine_minimum: bool = True

    reference_index: int = 0
    signal_config: SignalConfig = DEFAULT_SIGNAL_CONFIG


@dataclass(frozen=True)
class PairSearchResult:
    microphone_index: int
    true_tdoa_seconds: float
    estimated_tdoa_seconds: float
    search_result: ResidualSearchResult


@dataclass(frozen=True)
class SimulationResult3D:
    geometry: ArrayGeometry
    true_arrival_times_seconds: np.ndarray
    true_tdoa_seconds: np.ndarray
    estimated_tdoa_seconds: np.ndarray
    localization_result: LocalizationResult3D
    position_error_mm: float
    microphone_signals: np.ndarray
    time_axis: np.ndarray
    pair_results: list[PairSearchResult]


def validate_simulation_3d_config(
    config: AnalogSimulation3DConfig,
) -> None:
    if config.duration_seconds <= 0:
        raise ValueError("duration_seconds يجب أن تكون موجبة")

    if config.numerical_points < 200:
        raise ValueError("numerical_points يجب ألا تقل عن 200")

    if config.min_search_delay_seconds < 0:
        raise ValueError("min_search_delay_seconds لا يمكن أن تكون سالبة")

    if config.max_search_delay_seconds <= config.min_search_delay_seconds:
        raise ValueError("نطاق البحث عن التأخير غير صحيح")

    if config.search_points < 3:
        raise ValueError("search_points يجب ألا تقل عن 3")

    if len(config.channel_gains) != 4:
        raise ValueError("channel_gains يجب أن تحتوي 4 قيم")

    if len(config.channel_noise_stds) != 4:
        raise ValueError("channel_noise_stds يجب أن تحتوي 4 قيم")

    if config.reference_index not in (0, 1, 2, 3):
        raise ValueError("reference_index يجب أن يكون من 0 إلى 3")


def build_microphone_signals(
    time: np.ndarray,
    geometry: ArrayGeometry,
    config: AnalogSimulation3DConfig,
    rng: np.random.Generator,
) -> tuple[np.ndarray, np.ndarray]:
    validate_geometry(geometry)

    source_function = lambda query_time: generate_continuous_signal(
        query_time,
        config=config.signal_config,
    )

    arrival_times = compute_arrival_times(geometry)
    signals = []

    for idx in range(4):
        channel_config = AnalogChannelConfig(
            gain=float(config.channel_gains[idx]),
            extra_delay_seconds=float(arrival_times[idx]),
            noise_std=float(config.channel_noise_stds[idx]),
            lowpass_cutoff_hz=config.lowpass_cutoff_hz,
        )

        signal = apply_analog_channel(
            time=time,
            source_function=source_function,
            config=channel_config,
            rng=rng,
        )
        signals.append(signal)

    return np.asarray(signals, dtype=np.float64), arrival_times


def estimate_tdoa_for_pairs(
    time: np.ndarray,
    microphone_signals: np.ndarray,
    true_arrival_times: np.ndarray,
    config: AnalogSimulation3DConfig,
) -> tuple[np.ndarray, list[PairSearchResult]]:
    ref_index = config.reference_index
    reference_signal = microphone_signals[ref_index]

    search_delays = np.linspace(
        config.min_search_delay_seconds,
        config.max_search_delay_seconds,
        config.search_points,
        dtype=np.float64,
    )

    estimated = []
    details: list[PairSearchResult] = []

    for idx in range(4):
        if idx == ref_index:
            continue

        observed_signal = microphone_signals[idx]
        search_result = search_minimum_residual(
            time=time,
            reference_signal=reference_signal,
            observed_signal=observed_signal,
            delays_seconds=search_delays,
            fit_gain=config.fit_gain,
            refine=config.refine_minimum,
        )

        estimated_delay = (
            float(search_result.refined_delay_seconds)
            if (
                config.refine_minimum
                and search_result.refined_delay_seconds is not None
            )
            else float(search_result.best_delay_seconds)
        )

        true_tdoa = float(true_arrival_times[idx] - true_arrival_times[ref_index])

        estimated.append(estimated_delay)
        details.append(
            PairSearchResult(
                microphone_index=idx,
                true_tdoa_seconds=true_tdoa,
                estimated_tdoa_seconds=estimated_delay,
                search_result=search_result,
            )
        )

    return np.asarray(estimated, dtype=np.float64), details


def run_simulation_3d(
    geometry: ArrayGeometry,
    config: AnalogSimulation3DConfig | None = None,
    random_seed: int = 42,
) -> SimulationResult3D:
    if config is None:
        config = AnalogSimulation3DConfig()

    validate_simulation_3d_config(config)
    validate_geometry(geometry)

    rng = np.random.default_rng(random_seed)

    time = create_time_axis(
        start=0.0,
        stop=config.duration_seconds,
        points=config.numerical_points,
    )

    microphone_signals, arrival_times = build_microphone_signals(
        time=time,
        geometry=geometry,
        config=config,
        rng=rng,
    )

    true_tdoa = compute_tdoa_against_reference(
        arrival_times,
        reference_index=config.reference_index,
    )

    estimated_tdoa, pair_results = estimate_tdoa_for_pairs(
        time=time,
        microphone_signals=microphone_signals,
        true_arrival_times=arrival_times,
        config=config,
    )

    localization = solve_3d_source_position(
        geometry=geometry,
        measured_tdoa_seconds=estimated_tdoa,
        reference_index=config.reference_index,
    )

    pos_error_mm = position_error_millimeters(
        true_position=geometry.source_position,
        estimated_position=localization.estimated_position,
    )

    return SimulationResult3D(
        geometry=geometry,
        true_arrival_times_seconds=arrival_times,
        true_tdoa_seconds=true_tdoa,
        estimated_tdoa_seconds=estimated_tdoa,
        localization_result=localization,
        position_error_mm=pos_error_mm,
        microphone_signals=microphone_signals,
        time_axis=time,
        pair_results=pair_results,
    )
