# Integrated Design: Four-Microphone Magnetic Tape TDOA System

## Project Goal

Design and document a complete analog system that:

- Records four microphones simultaneously on a closed magnetic tape loop.
- Uses four parallel tape tracks.
- Reads all tracks with fixed playback heads.
- Measures time differences of arrival (TDOA) using analog residual-energy minimization.
- Estimates the direction or position of a sound source.

## System Overview

```text
4 Microphones
↓
4 Preamplifiers
↓
4 Analog Recording Gates (common Arduino control)
↓
4-track Record Head
↓
4 parallel magnetic tracks on a single tape
↓
Closed tape loop
↓
4-track Playback Head
↓
4 Read Preamplifiers + Gain Trim
↓
Analog TDOA Processing:
  - Reference channel selection
  - Delay compensation (mechanical or electronic)
  - Subtraction
  - Squaring
  - Integration
↓
Energy minima → TDOA estimates
↓
Localization algorithm (Arduino or external PC)
↓
Erase heads → tape ready for next frame
```

## Design Philosophy

- **Proof of concept first**: validate the residual-energy principle with two channels.
- **Integrated design second**: extend to four channels with full mechanical, electrical, and algorithmic documentation.
- **Analog core**: keep the signal path analog up to the energy measurement.
- **Digital control only**: use Arduino for timing, frame control, and optional localization math.

## Folder Contents

- `four_microphone_geometry.md`: microphone array geometry and localization equations.
- `four_track_tape_format.md`: tape format, frame structure, and timing.
- `analog_processing.md`: analog front-end, subtractor, squarer, integrator.
- `localization_model.md`: TDOA-to-position model and error analysis.
- `calibration_plan.md`: calibration procedure for gains, delays, and heads.
- `accuracy_budget.md`: theoretical accuracy limits and error sources.

> **Note**: The bill of materials is located at [`../hardware/bill_of_materials.csv`](../hardware/bill_of_materials.csv), not inside this folder.

## Status

This is a **proposed integrated design**. The residual-energy principle is validated in simulation and simplified analog experiments. The four-microphone hardware has not yet been built; this documentation provides the complete blueprint for implementation.
