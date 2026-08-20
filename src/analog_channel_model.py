"""
نموذج القناة التناظرية.

يدعم:
- الكسب.
- التأخير المستمر.
- مرشح منخفض التمرير من الدرجة الأولى.
- ضوضاء خرج القناة.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

import numpy as np


@dataclass(frozen=True)
class AnalogChannelConfig:
    """إعدادات قناة تناظرية واحدة."""

    gain: float = 1.0

    extra_delay_seconds: float = 0.0

    noise_std: float = 0.0

    # إذا كانت None فلن يطبق مرشح.
    lowpass_cutoff_hz: float | None = None


def validate_channel_config(
    config: AnalogChannelConfig,
) -> None:
    """التحقق من صحة إعدادات القناة."""
    if config.gain <= 0:
        raise ValueError(
            "gain يجب أن تكون أكبر من صفر"
        )

    if config.extra_delay_seconds < 0:
        raise ValueError(
            "extra_delay_seconds لا يمكن أن تكون سالبة"
        )

    if config.noise_std < 0:
        raise ValueError(
            "noise_std لا يمكن أن تكون سالبة"
        )

    if (
        config.lowpass_cutoff_hz is not None
        and config.lowpass_cutoff_hz <= 0
    ):
        raise ValueError(
            "lowpass_cutoff_hz يجب أن تكون أكبر من صفر"
        )


def apply_first_order_lowpass(
    time: np.ndarray,
    signal: np.ndarray,
    cutoff_hz: float,
) -> np.ndarray:
    """
    تطبيق مرشح منخفض التمرير تناظري من الدرجة الأولى.

    المعادلة التقريبية:
        y[n] = y[n-1] + alpha * (x[n] - y[n-1])

    حيث:
        alpha = dt / (tau + dt)
        tau = 1 / (2*pi*fc)
    """
    if cutoff_hz <= 0:
        raise ValueError(
            "cutoff_hz يجب أن تكون أكبر من صفر"
        )

    if time.ndim != 1 or signal.ndim != 1:
        raise ValueError(
            "time و signal يجب أن يكونا أحاديي البعد"
        )

    if time.shape != signal.shape:
        raise ValueError(
            "time و signal يجب أن تكون لهما نفس الأبعاد"
        )

    if time.size < 2:
        return signal.copy()

    tau = 1.0 / (
        2.0 * np.pi * cutoff_hz
    )

    filtered = np.empty_like(
        signal,
        dtype=np.float64,
    )

    filtered[0] = signal[0]

    for index in range(1, time.size):
        dt = time[index] - time[index - 1]

        if dt <= 0:
            raise ValueError(
                "محور الزمن يجب أن يكون متزايدًا"
            )

        alpha = dt / (tau + dt)

        filtered[index] = (
            filtered[index - 1]
            + alpha
            * (
                signal[index]
                - filtered[index - 1]
            )
        )

    return filtered


def apply_analog_channel(
    time: np.ndarray,
    source_function: Callable[
        [np.ndarray],
        np.ndarray,
    ],
    config: AnalogChannelConfig,
    rng: np.random.Generator | None = None,
) -> np.ndarray:
    """
    تمرير المصدر عبر القناة التناظرية.

    ترتيب العمليات:

        مصدر مستمر
        → تأخير مستمر
        → كسب
        → مرشح منخفض التمرير
        → ضوضاء
    """
    validate_channel_config(config)

    time = np.asarray(
        time,
        dtype=np.float64,
    )

    if time.ndim != 1:
        raise ValueError(
            "time يجب أن يكون متجهًا أحادي البعد"
        )

    if time.size < 2:
        raise ValueError(
            "time يجب أن يحتوي على نقطتين على الأقل"
        )

    if rng is None:
        rng = np.random.default_rng()

    delayed_time = (
        time
        - config.extra_delay_seconds
    )

    source_signal = np.asarray(
        source_function(delayed_time),
        dtype=np.float64,
    )

    if source_signal.shape != time.shape:
        raise ValueError(
            "source_function يجب أن تعيد "
            "إشارة بنفس شكل time"
        )

    channel_signal = (
        config.gain * source_signal
    )

    if config.lowpass_cutoff_hz is not None:
        channel_signal = (
            apply_first_order_lowpass(
                time=time,
                signal=channel_signal,
                cutoff_hz=(
                    config.lowpass_cutoff_hz
                ),
            )
        )

    if config.noise_std > 0:
        noise = rng.normal(
            loc=0.0,
            scale=config.noise_std,
            size=time.shape,
        )

        channel_signal = (
            channel_signal + noise
        )

    return channel_signal