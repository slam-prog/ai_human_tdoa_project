# Calibration Procedure

## Objectives

- Match gains across channels.
- Measure and compensate fixed delays.
- Verify simultaneous recording.
- Validate TDOA estimation.

## Prerequisites

- Signal generator.
- Oscilloscope.
- Known sound source (speaker).
- Measurement microphone (reference).

## Steps

### 1. Electrical Calibration

1. Inject identical test signals into both preamplifiers.
2. Adjust gain trims for equal output levels.
3. Verify phase and polarity.

### 2. Head Alignment

1. Record a common test tone on both tracks.
2. Measure relative delays between playback channels.
3. Adjust head positions to minimize fixed offsets.

### 3. Gate Timing

1. Trigger Arduino Gate with a known pattern.
2. Verify simultaneous opening/closing of both gates.
3. Check for skew in recorded edges.

### 4. TDOA Calibration

1. Place a sound source at a known position.
2. Measure TDOAs using energy minimization.
3. Compare with theoretical values.
4. Store calibration offsets.

### 5. Full-System Test

1. Move the source to multiple known positions.
2. Run localization algorithm.
3. Compare estimated positions with ground truth.
4. Document errors.

## Documentation

Record all calibration settings, measured delays, and test results for future reference.