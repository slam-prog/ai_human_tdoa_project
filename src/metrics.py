"""
حساب المقاييس الإحصائية لنتائج المحاكاة.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

#from .analog_simulation import TrialResult
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .analog_simulation import TrialResult

@dataclass(frozen=True)
class MetricsSummary:
    """ملخص أداء المحاكاة."""

    number_of_trials: int

    mean_absolute_timing_error_us: float
    median_absolute_timing_error_us: float

    mean_distance_error_mm: float
    median_distance_error_mm: float

    percentile_90_distance_error_mm: float
    percentile_95_distance_error_mm: float

    maximum_distance_error_mm: float

    errors_below_1_mm: int
    errors_above_1_mm: int


def calculate_metrics(
    results: list[TrialResult],
) -> MetricsSummary:
    """حساب المقاييس الأساسية."""
    if not results:
        raise ValueError(
            "لا توجد نتائج لحساب المقاييس"
        )

    timing_errors_us = np.array(
        [
            result.timing_error_microseconds
            for result in results
        ],
        dtype=np.float64,
    )

    distance_errors_mm = np.array(
        [
            result.distance_error_millimeters
            for result in results
        ],
        dtype=np.float64,
    )

    absolute_timing_errors_us = (
        np.abs(timing_errors_us)
    )

    errors_below_1_mm = int(
        np.sum(distance_errors_mm <= 1.0)
    )

    errors_above_1_mm = int(
        np.sum(distance_errors_mm > 1.0)
    )

    return MetricsSummary(
        number_of_trials=len(results),

        mean_absolute_timing_error_us=float(
            np.mean(absolute_timing_errors_us)
        ),

        median_absolute_timing_error_us=float(
            np.median(absolute_timing_errors_us)
        ),

        mean_distance_error_mm=float(
            np.mean(distance_errors_mm)
        ),

        median_distance_error_mm=float(
            np.median(distance_errors_mm)
        ),

        percentile_90_distance_error_mm=float(
            np.percentile(
                distance_errors_mm,
                90,
            )
        ),

        percentile_95_distance_error_mm=float(
            np.percentile(
                distance_errors_mm,
                95,
            )
        ),

        maximum_distance_error_mm=float(
            np.max(distance_errors_mm)
        ),

        errors_below_1_mm=errors_below_1_mm,
        errors_above_1_mm=errors_above_1_mm,
    )


def print_metrics(
    metrics: MetricsSummary,
) -> None:
    """طباعة ملخص المقاييس."""
    print("\n" + "=" * 72)
    print("Metrics Summary")
    print("=" * 72)

    print(
        "عدد التجارب: "
        f"{metrics.number_of_trials}"
    )

    print(
        "متوسط الخطأ المطلق زمنيًا: "
        f"{metrics.mean_absolute_timing_error_us:.6f} us"
    )

    print(
        "الوسيط الزمني المطلق: "
        f"{metrics.median_absolute_timing_error_us:.6f} us"
    )

    print(
        "متوسط خطأ المسافة: "
        f"{metrics.mean_distance_error_mm:.6f} mm"
    )

    print(
        "وسيط خطأ المسافة: "
        f"{metrics.median_distance_error_mm:.6f} mm"
    )

    print(
        "النسبة المئوية 90 للمسافة: "
        f"{metrics.percentile_90_distance_error_mm:.6f} mm"
    )

    print(
        "النسبة المئوية 95 للمسافة: "
        f"{metrics.percentile_95_distance_error_mm:.6f} mm"
    )

    print(
        "أقصى خطأ مسافة: "
        f"{metrics.maximum_distance_error_mm:.6f} mm"
    )

    print(
        "عدد النتائج تحت 1 مم: "
        f"{metrics.errors_below_1_mm}"
    )

    print(
        "عدد النتائج فوق 1 مم: "
        f"{metrics.errors_above_1_mm}"
    )