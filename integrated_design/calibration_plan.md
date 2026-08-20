# Calibration Plan

## Objectives

- Match gains across all four channels.
- Measure and compensate fixed delays between heads.
- Verify simultaneous recording.
- Validate TDOA estimation with known sources.

## Steps

### 1. Electrical Calibration

1. Inject the same test signal into all four preamplifiers.
2. Adjust gain trims so that all four readback levels are equal.
3. Verify phase and polarity of each channel.

### 2. Head Alignment

1. Record a common test tone on all four tracks.
2. Measure relative delays between playback channels.
3. Adjust mechanical positions of playback heads to minimize fixed offsets.

### 3. Gate Timing Verification

1. Trigger Arduino Gate with a known pattern.
2. Verify that all four recording gates open and close simultaneously.
3. Check for any skew in the recorded edges.

### 4. TDOA Calibration

1. Place a sound source at a known position.
2. Measure TDOAs using the analog energy-minimization method.
3. Compare measured TDOAs with theoretical values.
4. Store calibration offsets for each channel pair.

### 5. Full-System Test

1. Move the source to multiple known positions.
2. Run the localization algorithm.
3. Compare estimated positions with ground truth.
4. Document angular and positional errors.

## Documentation

Record:

- Gain settings.
- Head positions.
- Measured fixed delays.
- Calibration offsets.
- Test results for each configuration.