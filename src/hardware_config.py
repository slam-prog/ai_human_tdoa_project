from dataclasses import dataclass

@dataclass(frozen=True)
class HardwareConfig:
    speed_of_sound_m_s: float = 343.0
    frame_duration_s: float = 0.020
    inter_frame_gap_s: float = 0.005
    erase_pulse_s: float = 0.030
    sample_trigger_us: int = 100

DEFAULT_CONFIG = HardwareConfig()
