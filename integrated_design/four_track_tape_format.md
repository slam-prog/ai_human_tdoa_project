# Four-Track Tape Format

## Tape Configuration

- Single magnetic layer.
- Four parallel audio tracks on the same side.
- Closed-loop tape.
- Unidirectional motion.

Track assignment:

```text
Track 1 → Mic 1
Track 2 → Mic 2
Track 3 → Mic 3
Track 4 → Mic 4
```

All tracks are recorded simultaneously during the same Arduino Gate interval.

## Frame Structure

Each frame on the tape consists of:

```text
[Guard Gap]
[Sync / Frame ID (optional dedicated track or embedded)]
[Guard Gap]
[Audio Frame: Mic 1, Mic 2, Mic 3, Mic 4]
[Guard Gap]
```

On the four audio tracks:

```text
Track 1: [Guard][Mic 1 Audio][Guard]
Track 2: [Guard][Mic 2 Audio][Guard]
Track 3: [Guard][Mic 3 Audio][Guard]
Track 4: [Guard][Mic 4 Audio][Guard]
```

Optional sync track:

```text
Track 5 (if available): [Sync Pulse][Frame ID][Guard]
```

## Timing Parameters (Initial Proposal)

Example values for the first prototype:

```text
Tape speed: 0.5 m/s
Audio frame duration: 20 ms
Guard gap before frame: 5 ms
Guard gap after frame: 5 ms
Total frame period: 30 ms
Frame spatial length: 0.5 × 0.030 = 15 mm
```

Number of frames per meter of tape:

\[
N_\text{frames} \approx \frac{1000\ \text{mm}}{15\ \text{mm}} \approx 66\ \text{frames}
\]

For a 1 m loop, this gives roughly 60–65 usable frames after accounting for the splice and mechanical margins.

## Arduino Timing

Arduino generates:

```text
RECORD_GATE: HIGH during audio recording
SAMPLE_PULSE: short pulse after integration
ERASE_GATE: HIGH after processing is complete
SYNC_CONTROL: optional frame marker
```

All four recording gates are driven by the same `RECORD_GATE` signal, ensuring simultaneous start and stop.

## Erase and Reuse

Tape sequence for a given segment:

```text
Erase → Record → Buffer → Playback → Process → Erase → ...
```

The erase head is placed after the processing section so that each segment is erased just before being re-recorded in the next loop cycle.

## Track Width and Spacing

Exact track width and spacing depend on:

- Tape width.
- Head geometry.
- Desired crosstalk level.

For a standard cassette-style tape, four tracks will be narrower than the usual two-track-per-direction format, so crosstalk must be evaluated experimentally.