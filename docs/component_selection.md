# Component Selection

## Project Version

Prototype version 1.

The system uses:

- Arduino Uno R3.
- 5 V logic and analog supply.
- Two identical analog electret microphones.
- Two independent magnetic tape tracks.
- Synchronous recording of both microphones.
- Analog subtraction.
- Analog energy measurement.
- Closed magnetic tape loop.

---

## Main Controller

### Arduino Uno R3

Quantity:

```text
1
```

Functions:

- Generate the recording Gate signal.
- Open both recording channels simultaneously.
- Close both recording channels simultaneously.
- Count frames.
- Generate synchronization pulses.
- Control erase timing.
- Control Sample-and-Hold timing.

The Arduino does not process the audio signal.

The Arduino output controls analog switches and timing circuits only.

---

## Microphones

### CUI CMA-4544PF-W

Quantity:

```text
2
```

Configuration:

```text
Mic 1 = CMA-4544PF-W
Mic 2 = CMA-4544PF-W
```

Reason for selection:

- Analog output.
- Same model for both channels.
- Suitable for a 5 V prototype.
- Wide audio frequency response.
- Low cost and easy replacement.

Each microphone requires:

```text
Bias resistor
AC coupling capacitor
Low-noise preamplifier
```

The microphones must be mechanically separated and mounted in a stable position.

---

## Operational Amplifier

### Texas Instruments TLV9062

Quantity:

```text
5 ICs
```

Each IC contains two operational amplifiers.

Suggested allocation:

```text
U1A: Microphone 1 preamplifier
U1B: Microphone 2 preamplifier

U2A: Playback preamplifier 1
U2B: Playback preamplifier 2

U3A: Gain control channel 1
U3B: Gain control channel 2

U4A: Difference amplifier
U4B: Energy integrator

U5A: Vmid buffer
U5B: Sample-and-Hold buffer
```

Supply:

```text
VCC = +5 V
GND = 0 V
Vmid = approximately 2.5 V
```

All audio signals are biased around:

```text
Vmid = 2.5 V
```

because the prototype uses single-supply operation.

---

## Analog Recording Gates

### Analog Switch

Preferred component:

```text
ADG884
```

Quantity:

```text
2
```

Suggested use:

```text
ADG884 channel 1:
Mic 1 recording gate

ADG884 channel 2:
Mic 2 recording gate
```

Both switches receive the same Arduino Gate signal.

Logic:

```text
Gate = HIGH:
Recording enabled

Gate = LOW:
Recording disabled
```

The Arduino must not drive the tape head directly.

The signal path is:

```text
Microphone
→ Preamplifier
→ Analog Switch
→ Record Driver
→ Record Head
```

---

## Analog Squarer

Preferred component:

```text
ADL5391
```

Quantity:

```text
1
```

Function:

```text
Verror → Verror²
```

The ADL5391 is reserved for the accurate energy-measurement stage.

Because its package is difficult to solder manually, use:

```text
Breakout board
```

or assemble it on a professionally manufactured PCB.

Temporary alternative for the first electrical test:

```text
Precision rectifier + integrator
```

This alternative measures an absolute-value type quantity rather than exact squared energy. It is acceptable only for the first signal-path test.

---

## Energy Integrator

Use one TLV9062 amplifier with:

```text
Input resistor
Feedback capacitor
Parallel discharge resistor
```

The practical integrator is:

```text
V² signal
→ R input
→ Op-Amp
→ C feedback
```

A resistor in parallel with the capacitor prevents long-term saturation.

The integration window is controlled by Arduino or by an analog gate.

---

## Sample and Hold

The energy value for each frame is held after the integration window.

Required blocks:

```text
Integrator output
→ Analog switch
→ Hold capacitor
→ Buffer
```

The Arduino generates a short Sample pulse at the end of each valid frame.

---

## Tape Heads

The exact part number is not selected yet.

Required configuration:

```text
Two identical record heads
Two identical playback heads
Two identical erase heads
```

All heads must match:

- Tape width.
- Track width.
- Magnetic gap.
- Mechanical mounting.
- Head height.
- Azimuth angle.
- Tape contact surface.

Preferred source:

```text
Two identical heads recovered from the same tape transport
```

The final head choice must be made before designing the record-driver and erase-driver circuits.

---

## Tape Tracks

The tape uses two parallel audio tracks:

```text
Track 1 = Microphone 1
Track 2 = Microphone 2
```

Both tracks are recorded simultaneously.

The tape loop is:

```text
Record
→ Buffer
→ Playback
→ Energy Processing
→ Erase
→ Return to Record
```

---

## Power Supply

Main analog supply:

```text
+5 V regulated
```

Recommended current capacity for the prototype:

```text
At least 1 A
```

Arduino USB power should not be used to power:

- Motor.
- Record-head driver.
- Erase-head driver.
- High-current analog stages.

Use a separate regulated supply and connect the grounds at one controlled point.

---

## Required Decoupling

For every IC:

```text
100 nF ceramic capacitor close to VCC/GND pins
```

For each analog section:

```text
10 µF to 47 µF bulk capacitor
```

Keep the motor supply physically separate from the low-level playback preamplifiers.

---

## Not Yet Finalized

The following require mechanical measurements:

- Record-head model.
- Playback-head model.
- Erase-head model.
- Tape width.
- Track width.
- Head spacing.
- Tape speed.
- Motor voltage.
- Record bias frequency.
- Erase current.
- Record-head drive amplitude.