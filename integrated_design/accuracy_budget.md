# Accuracy Budget

## TDOA Error Sources

- Tape speed variation.
- Head gap and alignment errors.
- Crosstalk between tracks.
- Amplifier noise and mismatch.
- Squarer and integrator nonlinearity.
- Quantization of delay steps (mechanical or electronic).

## Theoretical Limits

For a TDOA error \(\sigma_t\):

\[
\sigma_r = c \sigma_t
\]

Examples:

| \(\sigma_t\) | \(\sigma_r\) (approx.) |
|-------------|------------------------|
| 1 µs        | 0.343 mm               |
| 10 µs       | 3.43 mm                |
| 100 µs      | 34.3 mm                |
| 1 ms        | 343 mm                 |

Position error depends on array geometry and source direction in addition to \(\sigma_r\).

## Target Specifications (Initial)

- TDOA resolution: ≤ 50 µs.
- Angular error (2D): ≤ 5° for far-field sources.
- Position error (3D, future): ≤ 10 cm within a few meters.

These targets will be refined after experimental characterization of the tape system.