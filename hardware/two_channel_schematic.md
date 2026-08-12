# Two-Channel Schematic

## Purpose

This schematic documents the two-channel proof-of-concept system, which validates the residual-energy principle for TDOA estimation.

## Signal Chain

### Channel 1 (Reference)

```text
Mic 1 → Preamp 1 → Gate 1 → Record Driver 1 → Head 1 → Tape
```

### Channel 2 (Delayed)

```text
Mic 2 → Preamp 2 → Gate 2 → Record Driver 2 → Head 2 → Tape
```

### Playback and Processing

```text
Head 1 → Preamp 1 → Gain 1 ─┐
                             ├→ Subtractor → Squarer → Integrator → Output
Head 2 → Preamp 2 → Gain 2 ─┘
```

## Components

- **Op-amps**: TLV9062 (dual, 5.5 V, 10 MHz).
- **Analog switches**: ADG884 (dual SPDT).
- **Multiplier**: ADL5391 (or discrete alternative for prototyping).
- **Microphones**: CUI CMA-4544PF-W (matched pair).

## Arduino Control

- `D8`: RECORD_GATE (common to both channels).
- `D9`: SAMPLE_PULSE (for energy capture).
- `D10`: ERASE_GATE (for tape erasure).

## Notes

- All audio signals are biased around V_MID ≈ 2.5 V.
- Use matched resistors (0.1%) for the subtractor.
- Ensure simultaneous gate operation for both channels.