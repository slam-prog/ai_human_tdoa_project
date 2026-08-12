"""
اختبار تحمل المحاكاة عبر عدة قيم للكسب والضوضاء.

يتم اختبار:

    channel_2_gain
    channel_1_noise_std
    channel_2_noise_std

ثم حساب:

    متوسط خطأ المسافة
    95% من الخطأ
    أقصى خطأ
    نسبة الفشل فوق 1 مم
    نسبة النجاح تحت أو تساوي 1 مم

وتحفظ النتائج في CSV ورسومات PNG.
"""

from __future__ import annotations

import csv
import io
from contextlib import redirect_stdout
from dataclasses import replace
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from .analog_simulation import (
    AnalogSimulationConfig,
    run_simulation,
)
from .metrics import calculate_metrics


OUTPUT_DIRECTORY = Path("results")


GAIN_VALUES = np.array(
    [
        1.00,
        0.98,
        0.95,
        0.90,
        0.85,
        0.80,
    ],
    dtype=np.float64,
)


NOISE_VALUES = np.array(
    [
        0.001,
        0.010,
        0.030,
        0.050,
        0.075,
        0.100,
    ],
    dtype=np.float64,
)


BASE_CONFIG = AnalogSimulationConfig(
    duration_seconds=0.004,
    numerical_points=40_000,

    min_true_delay_seconds=5.0e-6,
    max_true_delay_seconds=20.0e-6,

    min_search_delay_seconds=0.0,
    max_search_delay_seconds=30.0e-6,
    search_points=601,

    trials=20,

    channel_1_gain=1.0,
    channel_2_gain=0.95,

    channel_1_noise_std=0.03,
    channel_2_noise_std=0.03,

    fit_gain=False,
    refine_minimum=True,

    random_seed=42,
)


def run_single_case(
    gain: float,
    noise_std: float,
    case_index: int,
) -> dict[str, float]:
    """تشغيل حالة واحدة من حالات الاختبار."""

    config = replace(
        BASE_CONFIG,
        channel_2_gain=float(gain),
        channel_1_noise_std=float(noise_std),
        channel_2_noise_std=float(noise_std),
        random_seed=(
            BASE_CONFIG.random_seed
            + case_index * 1000
        ),
    )

    # إخفاء تفاصيل التجارب الداخلية.
    # نطبع فقط ملخص المسح النهائي.
    with redirect_stdout(io.StringIO()):
        results = run_simulation(config)

    metrics = calculate_metrics(results)

    total_trials = (
        metrics.number_of_trials
    )

    failure_rate = (
        metrics.errors_above_1_mm
        / total_trials
        * 100.0
    )

    success_rate = (
        metrics.errors_below_1_mm
        / total_trials
        * 100.0
    )

    return {
        "channel_2_gain": float(gain),
        "noise_std": float(noise_std),

        "trials": float(
            metrics.number_of_trials
        ),

        "mean_timing_error_us": float(
            metrics.mean_absolute_timing_error_us
        ),

        "median_timing_error_us": float(
            metrics.median_absolute_timing_error_us
        ),

        "mean_distance_error_mm": float(
            metrics.mean_distance_error_mm
        ),

        "median_distance_error_mm": float(
            metrics.median_distance_error_mm
        ),

        "percentile_90_distance_error_mm": float(
            metrics.percentile_90_distance_error_mm
        ),

        "percentile_95_distance_error_mm": float(
            metrics.percentile_95_distance_error_mm
        ),

        "maximum_distance_error_mm": float(
            metrics.maximum_distance_error_mm
        ),

        "success_rate_under_1mm_percent": float(
            success_rate
        ),

        "failure_rate_above_1mm_percent": float(
            failure_rate
        ),
    }


def save_csv(
    rows: list[dict[str, float]],
    output_path: Path,
) -> None:
    """حفظ نتائج المسح في ملف CSV."""

    if not rows:
        raise ValueError(
            "لا توجد نتائج لحفظها"
        )

    fieldnames = list(
        rows[0].keys()
    )

    with output_path.open(
        mode="w",
        newline="",
        encoding="utf-8",
    ) as csv_file:
        writer = csv.DictWriter(
            csv_file,
            fieldnames=fieldnames,
        )

        writer.writeheader()
        writer.writerows(rows)


def create_heatmap(
    values: np.ndarray,
    title: str,
    colorbar_label: str,
    output_path: Path,
    cmap: str,
) -> None:
    """إنشاء خريطة حرارية."""
    figure, axis = plt.subplots(
        figsize=(10, 7)
    )

    mesh = axis.pcolormesh(
        GAIN_VALUES,
        NOISE_VALUES,
        values,
        shading="auto",
        cmap=cmap,
    )

    colorbar = figure.colorbar(
        mesh,
        ax=axis,
    )

    colorbar.set_label(
        colorbar_label
    )

    axis.set_title(title)
    axis.set_xlabel(
        "Channel 2 Gain"
    )
    axis.set_ylabel(
        "Noise Standard Deviation"
    )

    axis.set_xticks(
        GAIN_VALUES
    )

    axis.set_yticks(
        NOISE_VALUES
    )

    axis.grid(
        visible=True,
        alpha=0.25,
    )

    figure.tight_layout()

    figure.savefig(
        output_path,
        dpi=160,
        bbox_inches="tight",
    )

    plt.close(figure)


def create_error_curves(
    mean_error_grid: np.ndarray,
    output_path: Path,
) -> None:
    """رسم متوسط الخطأ مقابل الكسب."""

    figure, axis = plt.subplots(
        figsize=(10, 7)
    )

    for row_index, noise in enumerate(
        NOISE_VALUES
    ):
        axis.plot(
            GAIN_VALUES,
            mean_error_grid[row_index],
            marker="o",
            linewidth=2,
            label=(
                f"noise={noise:g}"
            ),
        )

    axis.axhline(
        y=1.0,
        color="red",
        linestyle="--",
        linewidth=1.5,
        label="1 mm limit",
    )

    axis.set_title(
        "Mean Distance Error vs Channel 2 Gain"
    )

    axis.set_xlabel(
        "Channel 2 Gain"
    )

    axis.set_ylabel(
        "Mean Distance Error (mm)"
    )

    axis.grid(
        visible=True,
        alpha=0.3,
    )

    axis.legend()

    figure.tight_layout()

    figure.savefig(
        output_path,
        dpi=160,
        bbox_inches="tight",
    )

    plt.close(figure)


def run_sweep() -> list[dict[str, float]]:
    """تشغيل جميع حالات الكسب والضوضاء."""

    OUTPUT_DIRECTORY.mkdir(
        parents=True,
        exist_ok=True,
    )

    number_of_cases = (
        len(GAIN_VALUES)
        * len(NOISE_VALUES)
    )

    print("=" * 72)
    print("Robustness Sweep")
    print("=" * 72)
    print(
        f"عدد حالات الاختبار: "
        f"{number_of_cases}"
    )
    print(
        f"عدد التجارب لكل حالة: "
        f"{BASE_CONFIG.trials}"
    )
    print(
        "الحد المقبول للخطأ: "
        "1.000000 mm"
    )

    rows: list[dict[str, float]] = []

    mean_error_grid = np.zeros(
        (
            len(NOISE_VALUES),
            len(GAIN_VALUES),
        ),
        dtype=np.float64,
    )

    failure_rate_grid = np.zeros(
        (
            len(NOISE_VALUES),
            len(GAIN_VALUES),
        ),
        dtype=np.float64,
    )

    case_index = 0

    for noise_index, noise in enumerate(
        NOISE_VALUES
    ):
        for gain_index, gain in enumerate(
            GAIN_VALUES
        ):
            print(
                f"\nالحالة "
                f"{case_index + 1}/{number_of_cases}"
            )

            print(
                f"gain={gain:.3f}, "
                f"noise={noise:.3f}"
            )

            row = run_single_case(
                gain=float(gain),
                noise_std=float(noise),
                case_index=case_index,
            )

            rows.append(row)

            mean_error_grid[
                noise_index,
                gain_index,
            ] = row[
                "mean_distance_error_mm"
            ]

            failure_rate_grid[
                noise_index,
                gain_index,
            ] = row[
                "failure_rate_above_1mm_percent"
            ]

            print(
                "متوسط خطأ المسافة: "
                f"{row['mean_distance_error_mm']:.6f}"
                " mm"
            )

            print(
                "95% من الخطأ: "
                f"{row['percentile_95_distance_error_mm']:.6f}"
                " mm"
            )

            print(
                "نسبة النجاح تحت 1 مم: "
                f"{row['success_rate_under_1mm_percent']:.2f}%"
            )

            case_index += 1
        

    csv_path = (
        OUTPUT_DIRECTORY
        / "robustness_sweep.csv"
    )

    save_csv(
        rows=rows,
        output_path=csv_path,
    )
    worst_mean_case = max(
        rows,
        key=lambda row: (
            row["mean_distance_error_mm"]
        ),
    )

    worst_max_case = max(
        rows,
        key=lambda row: (
            row["maximum_distance_error_mm"]
        ),
    )

    worst_p95_case = max(
        rows,
        key=lambda row: (
            row[
                "percentile_95_distance_error_mm"
            ]
        ),
    )

    print("\n" + "=" * 72)
    print("أسوأ الحالات")
    print("=" * 72)

    print("\nأسوأ متوسط خطأ:")
    print(
        f"gain={worst_mean_case['channel_2_gain']:.3f}, "
        f"noise={worst_mean_case['noise_std']:.3f}"
    )
    print(
        "متوسط الخطأ: "
        f"{worst_mean_case['mean_distance_error_mm']:.6f}"
        " mm"
    )
    print(
        "95% من الخطأ: "
        f"{worst_mean_case['percentile_95_distance_error_mm']:.6f}"
        " mm"
    )
    print(
        "أقصى خطأ: "
        f"{worst_mean_case['maximum_distance_error_mm']:.6f}"
        " mm"
    )

    print("\nأسوأ قيمة قصوى:")
    print(
        f"gain={worst_max_case['channel_2_gain']:.3f}, "
        f"noise={worst_max_case['noise_std']:.3f}"
    )
    print(
        "أقصى خطأ مسجل: "
        f"{worst_max_case['maximum_distance_error_mm']:.6f}"
        " mm"
    )

    print("\nأسوأ نسبة مئوية 95:")
    print(
        f"gain={worst_p95_case['channel_2_gain']:.3f}, "
        f"noise={worst_p95_case['noise_std']:.3f}"
    )
    print(
        "النسبة المئوية 95: "
        f"{worst_p95_case['percentile_95_distance_error_mm']:.6f}"
        " mm"
    )

    mean_error_path = (
        OUTPUT_DIRECTORY
        / "mean_error_heatmap.png"
    )

    create_heatmap(
        values=mean_error_grid,
        title=(
            "Mean Distance Error"
        ),
        colorbar_label=(
            "Mean Error (mm)"
        ),
        output_path=mean_error_path,
        cmap="viridis",
    )

    failure_rate_path = (
        OUTPUT_DIRECTORY
        / "failure_rate_heatmap.png"
    )

    create_heatmap(
        values=failure_rate_grid,
        title=(
            "Failure Rate Above 1 mm"
        ),
        colorbar_label=(
            "Failure Rate (%)"
        ),
        output_path=failure_rate_path,
        cmap="magma",
    )

    curves_path = (
        OUTPUT_DIRECTORY
        / "mean_error_curves.png"
    )

    create_error_curves(
        mean_error_grid=mean_error_grid,
        output_path=curves_path,
    )

    print("\n" + "=" * 72)
    print("اكتمل اختبار التحمل")
    print("=" * 72)
    print(
        f"ملف CSV: {csv_path}"
    )
    print(
        f"رسم متوسط الخطأ: "
        f"{mean_error_path}"
    )
    print(
        f"رسم نسبة الفشل: "
        f"{failure_rate_path}"
    )
    print(
        f"رسم منحنيات الخطأ: "
        f"{curves_path}"
    )

    return rows



if __name__ == "__main__":
    run_sweep()
