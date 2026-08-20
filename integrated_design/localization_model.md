# Localization Model

## From TDOA to Position

Given:

- Microphone positions \(M_i\).
- Measured TDOAs \(\Delta t_{i1}\).
- Speed of sound \(c\).

Range differences:

\[
\Delta r_{i1} = c \Delta t_{i1}
\]

For a source at \(p=(x,y,z)\):

\[
\|p - M_i\| - \|p - M_1\| = \Delta r_{i1},\quad i=2,3,4
\]

This is a system of nonlinear equations in \((x,y,z)\).

## Solution Methods

### Linearized Least Squares

Linearize around an initial guess \(p_0\) and solve iteratively:

\[
J \Delta p \approx \Delta r
\]

Where \(J\) is the Jacobian of the range-difference equations.

Update:

\[
p_{k+1} = p_k + \Delta p
\]

Repeat until convergence.

### Closed-Form Approximations

For specific geometries (e.g., planar arrays with far-field sources), approximate direction cosines can be derived directly from TDOAs.

For a planar square array and far-field sources, the direction can be approximated from the TDOA ratios.

## Error Propagation

Let TDOA errors be \(\sigma_t\). Range-difference errors:

\[
\sigma_r = c \sigma_t
\]

Position error depends on:

- Array geometry.
- Source direction.
- Magnitude of \(\sigma_r\).

Well-conditioned geometries (e.g., tetrahedral) reduce sensitivity to TDOA errors compared to poorly conditioned ones (e.g., nearly collinear microphones).

## Implementation

- Arduino can perform a simplified 2D direction estimate.
- A PC or more powerful microcontroller can run full 3D localization.
- The analog front-end provides TDOA estimates; the digital back-end computes position.

## Performance Metrics

- Angular error (degrees) for direction finding.
- Position error (mm or cm) for 3D localization.
- Robustness to noise and multipath.

These metrics will be evaluated experimentally after hardware implementation.