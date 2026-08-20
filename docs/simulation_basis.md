# Simulation Basis

## Purpose

Document the theoretical foundation and simulation methodology for the TDOA estimation system.

## Mathematical Model

### Signal Model

For two microphones receiving the same source with delay \(\tau\):

\[
x_1(t) = s(t) + n_1(t)
\]
\[
x_2(t) = s(t - \tau) + n_2(t)
\]

Where:
- \(s(t)\): Source signal.
- \(n_1(t), n_2(t)\): Noise.

### Residual Energy

For a trial delay \(\tau'\):

\[
e(t; \tau') = x_1(t) - x_2(t - \tau')
\]
\[
E(\tau') = \int e^2(t; \tau') dt
\]

The true delay \(\tau\) minimizes \(E(\tau')\).

## Simulation Parameters

- **Sampling Rate**: 44.1 kHz (audio band).
- **Signal Types**: Speech, music, test tones.
- **Noise Levels**: Varied SNR conditions.
- **Delay Range**: 0–10 ms (typical for microphone arrays).

## Validation

Simulations validate:

- Correct delay recovery under ideal conditions.
- Robustness to noise and gain mismatch.
- Effect of bandwidth limitations.

## Results

See `results/` directory for simulation outputs and plots.