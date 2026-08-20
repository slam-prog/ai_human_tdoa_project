"""
حساب طاقة الفرق بين إشارتين تناظريتين محاكاتين.

الفكرة:
    1. نأخذ إشارة مرجعية.
    2. نغير تأخير الإشارة الثانية.
    3. نطرح الإشارتين.
    4. نربع الفرق.
    5. نكامل خلال نافذة زمنية.
    6. نبحث عن التأخير الذي يعطي أقل طاقة فرق.

التأخير هنا قيمة زمنية مستمرة في المحاكاة، وليس عددًا صحيحًا
من العينات.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class ResidualSearchResult:
    """نتيجة البحث عن أقل طاقة فرق."""

    best_delay_seconds: float
    minimum_energy: float
    delays_seconds: np.ndarray
    energies: np.ndarray
    refined_delay_seconds: float | None = None
    refined_energy: float | None = None


def _validate_time_and_signal(
    time: np.ndarray,
    signal: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    """التحقق من محور الزمن والإشارة."""
    time_array = np.asarray(time, dtype=np.float64)
    signal_array = np.asarray(signal, dtype=np.float64)

    if time_array.ndim != 1:
        raise ValueError(
            "time يجب أن تكون مصفوفة أحادية البعد"
        )

    if signal_array.ndim != 1:
        raise ValueError(
            "signal يجب أن تكون مصفوفة أحادية البعد"
        )

    if len(time_array) != len(signal_array):
        raise ValueError(
            "يجب أن يتساوى طول time و signal"
        )

    if len(time_array) < 2:
        raise ValueError(
            "يلزم وجود نقطتين زمنيتين على الأقل"
        )

    time_differences = np.diff(time_array)

    if np.any(time_differences <= 0):
        raise ValueError(
            "يجب أن يكون time مرتبًا تصاعديًا دون تكرار"
        )

    if not np.all(np.isfinite(time_array)):
        raise ValueError(
            "time يحتوي على قيم غير صالحة"
        )

    if not np.all(np.isfinite(signal_array)):
        raise ValueError(
            "signal يحتوي على قيم غير صالحة"
        )

    return time_array, signal_array


def interpolate_signal(
    time: np.ndarray,
    signal: np.ndarray,
    query_time: np.ndarray,
) -> np.ndarray:
    """
    تقييم الإشارة عند أزمنة جديدة باستخدام interpolation خطي.

    خارج نطاق time نعيد صفرًا، لأن نافذة التسجيل لا تحتوي
    إشارة خارج مجالها.
    """
    time_array, signal_array = _validate_time_and_signal(
        time,
        signal,
    )

    query_array = np.asarray(
        query_time,
        dtype=np.float64,
    )

    return np.interp(
        query_array,
        time_array,
        signal_array,
        left=0.0,
        right=0.0,
    )


def compensate_delay(
    time: np.ndarray,
    observed_signal: np.ndarray,
    compensation_delay_seconds: float,
) -> np.ndarray:
    """
    تعويض تأخير إشارة.

    إذا كانت observed_signal متأخرة عن المرجع بمقدار τ،
    فإن تمرير compensation_delay_seconds = τ يجعلنا نقرأ
    الإشارة عند time + τ، أي نعيدها زمنيًا إلى الأمام.

    لذلك:
        observed(t) = source(t - τ)
        observed(t + τ) = source(t)
    """
    time_array, signal_array = _validate_time_and_signal(
        time,
        observed_signal,
    )

    if not np.isfinite(compensation_delay_seconds):
        raise ValueError(
            "compensation_delay_seconds يجب أن يكون finite"
        )

    query_time = (
        time_array + compensation_delay_seconds
    )

    return interpolate_signal(
        time_array,
        signal_array,
        query_time,
    )


def calculate_residual_energy(
    time: np.ndarray,
    reference_signal: np.ndarray,
    observed_signal: np.ndarray,
    compensation_delay_seconds: float,
    fit_gain: bool = False,
) -> float:
    """
    حساب طاقة الفرق بعد تعويض تأخير محدد.

    Args:
        time:
            محور الزمن بالثواني.
        reference_signal:
            الإشارة المرجعية.
        observed_signal:
            الإشارة التي نبحث عن تأخيرها.
        compensation_delay_seconds:
            التأخير الذي سنجربه لتعويض الإشارة الثانية.
        fit_gain:
            إذا كان True، نقدر كسبًا خطيًا للإشارة الثانية
            قبل حساب الفرق لتقليل تأثير اختلاف سعة القنوات.

    Returns:
        متوسط طاقة الفرق خلال النافذة.
    """
    time_array, reference = _validate_time_and_signal(
        time,
        reference_signal,
    )

    _, observed = _validate_time_and_signal(
        time_array,
        observed_signal,
    )

    compensated = compensate_delay(
        time=time_array,
        observed_signal=observed,
        compensation_delay_seconds=(
            compensation_delay_seconds
        ),
    )

    if fit_gain:
        denominator = float(
            np.dot(compensated, compensated)
        )

        if denominator > 1e-20:
            gain = float(
                np.dot(reference, compensated)
                / denominator
            )
            compensated = gain * compensated

    residual = reference - compensated

    # تكامل طاقة الفرق باستخدام قاعدة شبه المنحرف.
    if hasattr(np, "trapezoid"):
        energy_integral = float(np.trapezoid(residual**2, time_array))
    else:
        energy_integral = float(np.trapz(residual**2, time_array))

    window_duration = (
        time_array[-1] - time_array[0]
    )

    if window_duration <= 0:
        raise ValueError(
            "مدة نافذة التكامل يجب أن تكون موجبة"
        )

    return energy_integral / window_duration


def refine_minimum_quadratic(
    delays_seconds: np.ndarray,
    energies: np.ndarray,
    minimum_index: int,
) -> tuple[float, float]:
    """
    تحسين موضع الحد الأدنى باستخدام منحنى تربيعي محلي.

    هذه الخطوة تسمح بتقدير قيمة بين نقاط البحث العددية.
    """
    delays = np.asarray(
        delays_seconds,
        dtype=np.float64,
    )

    values = np.asarray(
        energies,
        dtype=np.float64,
    )

    if len(delays) != len(values):
        raise ValueError(
            "يجب تساوي أطوال delays و energies"
        )

    if (
        minimum_index <= 0
        or minimum_index >= len(values) - 1
    ):
        return (
            float(delays[minimum_index]),
            float(values[minimum_index]),
        )

    x1 = delays[minimum_index - 1]
    x2 = delays[minimum_index]
    x3 = delays[minimum_index + 1]

    y1 = values[minimum_index - 1]
    y2 = values[minimum_index]
    y3 = values[minimum_index + 1]

    denominator = (
        y1 - 2.0 * y2 + y3
    )

    if abs(denominator) < 1e-30:
        return float(x2), float(y2)

    offset = 0.5 * (y1 - y3) / denominator

    spacing_left = x2 - x1
    spacing_right = x3 - x2

    if not np.isclose(
        spacing_left,
        spacing_right,
        rtol=1e-5,
        atol=1e-18,
    ):
        return float(x2), float(y2)

    refined_delay = x2 + offset * spacing_left

    refined_energy = (
        y2
        - 0.25 * (y1 - y3) * offset
    )

    return (
        float(refined_delay),
        float(refined_energy),
    )


def search_minimum_residual(
    time: np.ndarray,
    reference_signal: np.ndarray,
    observed_signal: np.ndarray,
    delays_seconds: np.ndarray,
    fit_gain: bool = False,
    refine: bool = True,
) -> ResidualSearchResult:
    """
    البحث عن التأخير الذي يعطي أقل طاقة فرق.

    Args:
        time:
            محور الزمن.
        reference_signal:
            الإشارة المرجعية.
        observed_signal:
            الإشارة المتأخرة.
        delays_seconds:
            قيم التأخير المراد اختبارها.
        fit_gain:
            تعويض اختلاف الكسب أثناء المقارنة.
        refine:
            تحسين الحد الأدنى بين نقاط البحث.

    Returns:
        ResidualSearchResult.
    """
    time_array, reference = _validate_time_and_signal(
        time,
        reference_signal,
    )

    _, observed = _validate_time_and_signal(
        time_array,
        observed_signal,
    )

    delays = np.asarray(
        delays_seconds,
        dtype=np.float64,
    )

    if delays.ndim != 1:
        raise ValueError(
            "delays_seconds يجب أن تكون أحادية البعد"
        )

    if len(delays) < 3:
        raise ValueError(
            "يلزم ثلاث قيم تأخير على الأقل"
        )

    if not np.all(np.isfinite(delays)):
        raise ValueError(
            "delays_seconds تحتوي على قيم غير صالحة"
        )

    energies = np.array(
        [
            calculate_residual_energy(
                time=time_array,
                reference_signal=reference,
                observed_signal=observed,
                compensation_delay_seconds=float(delay),
                fit_gain=fit_gain,
            )
            for delay in delays
        ],
        dtype=np.float64,
    )

    minimum_index = int(np.argmin(energies))

    best_delay = float(delays[minimum_index])
    best_energy = float(energies[minimum_index])

    refined_delay = None
    refined_energy = None

    if refine:
        (
            refined_delay,
            refined_energy,
        ) = refine_minimum_quadratic(
            delays_seconds=delays,
            energies=energies,
            minimum_index=minimum_index,
        )

    return ResidualSearchResult(
        best_delay_seconds=best_delay,
        minimum_energy=best_energy,
        delays_seconds=delays,
        energies=energies,
        refined_delay_seconds=refined_delay,
        refined_energy=refined_energy,
    )
