# System Block Diagram

## Signal Flow

```text
Microphones
    ↓
Preamplifiers
    ↓
Analog Recording Gates (Arduino-controlled)
    ↓
Record Drivers + Bias
    ↓
Record Heads (Multiple Tracks)
    ↓
Magnetic Tape (Closed Loop)
    ↓
Playback Heads
    ↓
Read Preamplifiers
    ↓
Gain Trim
    ↓
TDOA Processing:
    - Delay Compensation
    - Subtraction
    - Squaring
    - Integration
    ↓
Energy Minimization → TDOA Estimates
    ↓
Localization Algorithm
    ↓
Erase Heads → Tape Reuse
```

## Key Blocks

### Recording Section

- Microphones and preamplifiers.
- Analog switches (recording gates).
- Record drivers and bias oscillator.
- Record heads.

### Playback Section

- Playback heads.
- Read preamplifiers.
- Gain trim circuits.

### TDOA Processing

- Delay lines (mechanical or electronic).
- Difference amplifiers.
- Analog multipliers (squaring).
- Integrators.
- Sample-and-hold circuits.

### Control Section

- Arduino Uno for timing and frame control.
- Motor control (separate circuit).
- Erase control.

## Power Distribution

- 5 V analog supply for low-level circuits.
- Separate supply for motor and head drivers.
- Star grounding to minimize noise.