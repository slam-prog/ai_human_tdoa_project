"""
نموذج القناة التناظرية.

يمثل هذا الملف الاختلافات الواقعية بين قنوات الميكروفونات
ومسارات التسجيل والقراءة، دون استخدام ADC لتحديد التأخير.

العوامل المدعومة:
- كسب القناة.
- تأخير إضافي.
- Offset تناظري.
- ضوضاء.
- عكس القطبية اختياريًا.
- تشبع الجهد اختياريًا.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Optional

import numpy as np


ContinuousSignalFunction = Callable[[np.ndarray], np.ndarray]


@dataclass(frozen=True)
class AnalogChannelConfig:
    """
    إعدادات قناة تناظرية واحدة.

    Args:
        gain:
            كسب القناة.
        extra_delay_seconds:
            تأخير إضافي في مسار القناة بالثواني.
        dc_offset:
            انحياز مستمر يضاف إلى الإشارة.
        noise_std:
            الانحراف المعياري للضوضاء.
        polarity:
            قطبية القناة، وتكون 1 أو -1.
        saturation_limit:
            حد التشبع الموجب والسالب.
            إذا كانت None فلا يوجد تشبع.
    """

    gain: float = 1.0
    extra_delay_seconds: float = 0.0
    dc_offset: float = 0.0
    noise_std: float = 0.0
    polarity: float = 1.0
    saturation_limit: Optional[float] = None

    def validate(self) -> None:
        """التحقق من صحة إعدادات القناة."""
        values = {
            "gain": self.gain,
            "extra_delay_seconds": self.extra_delay_seconds,
            "dc_offset": self.dc_offset,
            "noise_std": self.noise_std,
            "polarity": self.polarity,
        }

        for name, value in values.items():
            if not np.isfinite(value):
                raise ValueError(
                    f"{name} يجب أن يكون قيمة finite"
                )

        if self.noise_std < 0:
            raise ValueError(
                "noise_std يجب ألا يكون سالبًا"
            )

        if self.polarity not in (-1.0, 1.0):
            raise ValueError(
                "polarity يجب أن تكون 1.0 أو -1.0"
            )

        if self.saturation_limit is not None:
            if not np.isfinite(self.saturation_limit):
                raise ValueError(
                    "saturation_limit يجب أن يكون قيمة finite"
                )

            if self.saturation_limit <= 0:
                raise ValueError(
                    "saturation_limit يجب أن يكون أكبر من صفر"
                )


def apply_analog_channel(
    time: np.ndarray,
    source_function: ContinuousSignalFunction,
    config: AnalogChannelConfig,
    rng: Optional[np.random.Generator] = None,
) -> np.ndarray:
    """
    تمرير إشارة مستمرة عبر نموذج قناة تناظرية.

    Args:
        time:
            محور الزمن بالثواني.
        source_function:
            دالة تعيد قيمة المصدر عند أي زمن.
        config:
            إعدادات القناة.
        rng:
            مولد ضوضاء قابل لإعادة الإنتاج.

    Returns:
        الإشارة الخارجة من القناة التناظرية.
    """
    config.validate()

    time_array = np.asarray(time, dtype=np.float64)

    if time_array.ndim != 1:
        raise ValueError(
            "time يجب أن تكون مصفوفة أحادية البعد"
        )

    if len(time_array) == 0:
        return np.array([], dtype=np.float64)

    delayed_time = (
        time_array - config.extra_delay_seconds
    )

    source = np.asarray(
        source_function(delayed_time),
        dtype=np.float64,
    )

    if source.shape != time_array.shape:
        raise ValueError(
            "source_function يجب أن تعيد نفس شكل time"
        )

    output = (
        config.polarity
        * config.gain
        * source
    )

    if config.dc_offset != 0.0:
        output = output + config.dc_offset

    if config.noise_std > 0.0:
        if rng is None:
            rng = np.random.default_rng()

        noise = rng.normal(
            loc=0.0,
            scale=config.noise_std,
            size=output.shape,
        )

        output = output + noise

    if config.saturation_limit is not None:
        limit = config.saturation_limit
        output = np.clip(output, -limit, limit)

    return output


def create_channel_pair(
    gain_1: float = 1.0,
    gain_2: float = 1.0,
    delay_1_seconds: float = 0.0,
    delay_2_seconds: float = 0.0,
    noise_std_1: float = 0.0,
    noise_std_2: float = 0.0,
) -> tuple[AnalogChannelConfig, AnalogChannelConfig]:
    """
    إنشاء إعدادات قناتين للمقارنة بين ميكروفونين.

    هذه الدالة مفيدة للمحاكاة لأنها تسمح بإدخال اختلافات
    مستقلة بين القناتين.
    """
    channel_1 = AnalogChannelConfig(
        gain=gain_1,
        extra_delay_seconds=delay_1_seconds,
        noise_std=noise_std_1,
    )

    channel_2 = AnalogChannelConfig(
        gain=gain_2,
        extra_delay_seconds=delay_2_seconds,
        noise_std=noise_std_2,
    )

    return channel_1, channel_2


def add_relative_gain_mismatch(
    signal: np.ndarray,
    mismatch_fraction: float,
) -> np.ndarray:
    """
    إضافة اختلاف كسب مباشر إلى إشارة موجودة.

    مثال:
        mismatch_fraction=0.01
        يعني زيادة السعة بنسبة 1%.
    """
    if not np.isfinite(mismatch_fraction):
        raise ValueError(
            "mismatch_fraction يجب أن يكون قيمة finite"
        )

    signal_array = np.asarray(signal, dtype=np.float64)

    return signal_array * (1.0 + mismatch_fraction)