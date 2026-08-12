# Analog Architecture

## System Overview

The analog architecture implements a TDOA estimation system using magnetic tape recording and residual energy minimization.

## Signal Path

### Recording Path

```text
Microphone → Preamplifier → Analog Switch → Record Driver → Record Head → Tape
```

### Playback Path

```text
Playback Head → Read Preamplifier → Gain Trim → TDOA Processing
```

## TDOA Processing

For each channel pair (reference, delayed):

1. **Delay Compensation**: Adjust relative timing (mechanical or electronic).
2. **Subtraction**: Compute difference signal.
3. **Squaring**: Square the difference.
4. **Integration**: Integrate over the frame duration.
5. **Energy Minimization**: Find delay that minimizes energy.

## Key Design Choices

- **Single-supply operation**: All signals biased around V_MID ≈ 2.5 V.
- **Matched components**: Critical for subtractor accuracy.
- **Analog core**: Processing remains analog up to energy measurement.
- **Digital control**: Arduino handles timing, not signal processing.

## Power Distribution

- 5 V regulated supply for analog circuits.
- Separate supply for motor and head drivers.
- Star grounding to minimize noise coupling.