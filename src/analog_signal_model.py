"""
نموذج الإشارة الصوتية المستمرة للمحاكاة التناظرية.

هذا الملف لا يحاكي ADC ولا يفرض أن التأخير عدد صحيح من العينات.
الإشارة معرفة كدالة زمنية يمكن تقييمها عند أي قيمة زمنية حقيقية.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class SignalConfig:
    """
    إعدادات الإشارة الصوتية التجريبية.

    جميع الأزمنة بالثواني والترددات بالهرتز.
    """

    duration: float = 0.004
    center_time: float = 0.002
    envelope_width: float = 0.00075

    base_frequency: float = 1800.0
    second_frequency: float = 4200.0
    third_frequency: float = 7600.0

    transient_time: float = 0.00215
    transient_width: float = 0.00008


DEFAULT_SIGNAL_CONFIG = SignalConfig()


def _gaussian_envelope(
    time: np.ndarray,
    center: float,
    width: float,
) -> np.ndarray:
    """إنشاء غلاف Gaussian زمني."""
    if width <= 0:
        raise ValueError("width يجب أن يكون أكبر من صفر")

    return np.exp(
        -0.5 * ((time - center) / width) ** 2
    )


def _safe_time_array(time: np.ndarray | float) -> np.ndarray:
    """تحويل الزمن إلى مصفوفة NumPy من نوع float."""
    return np.asarray(time, dtype=np.float64)


def generate_continuous_signal(
    time: np.ndarray | float,
    config: SignalConfig = DEFAULT_SIGNAL_CONFIG,
) -> np.ndarray:
    """
    تقييم منحنى صوتي مستمر عند الزمن المعطى.

    لا يوجد هنا مفهوم:
        integer delay
        sample index delay

    يمكن تمرير أي زمن حقيقي، مثل:
        0.0000123
        0.00001237

    Args:
        time:
            قيمة زمنية أو مصفوفة أزمنة بالثواني.
        config:
            إعدادات الإشارة.

    Returns:
        قيم الإشارة عند الأزمنة المطلوبة.
    """
    time_array = _safe_time_array(time)

    main_envelope = _gaussian_envelope(
        time_array,
        center=config.center_time,
        width=config.envelope_width,
    )

    carrier_1 = np.sin(
        2.0 * np.pi * config.base_frequency * time_array
    )

    carrier_2 = 0.35 * np.sin(
        2.0 * np.pi * config.second_frequency * time_array
        + 0.37
    )

    carrier_3 = 0.18 * np.sin(
        2.0 * np.pi * config.third_frequency * time_array
        - 0.61
    )

    # مكوّن قصير يشبه بداية حدث صوتي سريع.
    transient_envelope = _gaussian_envelope(
        time_array,
        center=config.transient_time,
        width=config.transient_width,
    )

    transient = 0.45 * transient_envelope * np.sin(
        2.0 * np.pi * 9800.0 * time_array
    )

    signal = (
        main_envelope * (carrier_1 + carrier_2 + carrier_3)
        + transient
    )

    # خارج نافذة الإشارة نعيد صفرًا.
    valid = (
        (time_array >= 0.0)
        & (time_array <= config.duration)
    )

    signal = np.where(valid, signal, 0.0)

    # تطبيع السعة.
    maximum = np.max(np.abs(signal))

    if maximum > 0:
        signal = signal / maximum

    return signal


def delayed_continuous_signal(
    time: np.ndarray | float,
    delay_seconds: float,
    gain: float = 1.0,
    config: SignalConfig = DEFAULT_SIGNAL_CONFIG,
) -> np.ndarray:
    """
    تقييم نسخة متأخرة من الإشارة عند تأخير حقيقي مستمر.

    مثال:
        delay_seconds = 12.37e-6

    هذا التأخير ليس عددًا صحيحًا من العينات.
    """
    if not np.isfinite(delay_seconds):
        raise ValueError("delay_seconds يجب أن يكون قيمة finite")

    if not np.isfinite(gain):
        raise ValueError("gain يجب أن يكون قيمة finite")

    time_array = _safe_time_array(time)

    return gain * generate_continuous_signal(
        time_array - delay_seconds,
        config=config,
    )


def create_time_axis(
    start: float = 0.0,
    stop: float = DEFAULT_SIGNAL_CONFIG.duration,
    points: int = 200_000,
) -> np.ndarray:
    """
    إنشاء محور زمني عالي الكثافة للتكامل العددي.

    مهم:
    points هنا دقة حسابية داخل المحاكاة فقط، وليس معدل عينات
    لجهاز ADC أو قيدًا للنظام التناظري المقترح.
    """
    if points < 2:
        raise ValueError("points يجب أن يكون 2 أو أكثر")

    if stop <= start:
        raise ValueError("stop يجب أن يكون أكبر من start")

    return np.linspace(
        start,
        stop,
        int(points),
        dtype=np.float64,
    )


def normalize_signal(signal: np.ndarray) -> np.ndarray:
    """تطبيع إشارة إلى المجال التقريبي [-1, 1]."""
    signal_array = np.asarray(signal, dtype=np.float64)
    maximum = np.max(np.abs(signal_array))

    if maximum <= 0:
        return signal_array.copy()

    return signal_array / maximum