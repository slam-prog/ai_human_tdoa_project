# Four-Microphone Geometry

## Objective

Define the spatial arrangement of the four microphones and derive the equations that map measured time differences to source direction or position.

## Coordinate System

Use a right-handed Cartesian system:

- X: horizontal axis.
- Y: horizontal axis, orthogonal to X.
- Z: vertical axis.

Speed of sound:

\[
c \approx 343\ \text{m/s at 20°C}
\]

## Planar Square Array (2D Direction Finding)

Initial recommended geometry:

```text
M1 ───────── M2
│             │
│      C      │
│             │
M4 ───────── M3
```

Microphone positions:

\[
M_1 = \left(+\frac{a}{2}, +\frac{a}{2}, 0\right)
\]

\[
M_2 = \left(-\frac{a}{2}, +\frac{a}{2}, 0\right)
\]

\[
M_3 = \left(-\frac{a}{2}, -\frac{a}{2}, 0\right)
\]

\[
M_4 = \left(+\frac{a}{2}, -\frac{a}{2}, 0\right)
\]

Where:

```text
a = side length of the square (e.g., 50–100 mm)
```

Reference microphone:

```text
M1
```

Measured time differences:

\[
\Delta t_{12},\ \Delta t_{13},\ \Delta t_{14}
\]

Corresponding range differences:

\[
\Delta r_{i1} = c \Delta t_{i1}
\]

For a source at position \(p=(x,y,z)\):

\[
\|p - M_i\| - \|p - M_1\| = c \Delta t_{i1},\quad i=2,3,4
\]

In the planar case with sources approximately in the same plane (\(z\approx 0\)), these equations can be solved for \((x,y)\).

## Tetrahedral Array (3D Localization)

For full 3D localization, use a non-coplanar arrangement, e.g., a tetrahedron:

```text
             M4
            /|\
           / | \
          /  |  \
        M1───┼───M2
          \  |  /
           \ | /
            \|/
             M3
```

Example coordinates (side length \(L\)):

\[
M_1 = \left(0, 0, 0\right)
\]

\[
M_2 = \left(L, 0, 0\right)
\]

\[
M_3 = \left(\frac{L}{2}, \frac{\sqrt{3}}{2}L, 0\right)
\]

\[
M_4 = \left(\frac{L}{2}, \frac{\sqrt{3}}{6}L, \sqrt{\frac{2}{3}}L\right)
\]

With four non-coplanar microphones, the system can in principle solve for \((x,y,z)\) of the source, provided the TDOA estimates are sufficiently accurate.

## Number of Independent TDOA Measurements

With \(N=4\) microphones and one reference:

- Independent TDOAs: \(N-1 = 3\).
- Total pairwise TDOAs: \(\frac{N(N-1)}{2} = 6\).

Using all six pairs can improve robustness, but the minimal design uses three TDOAs relative to M1.

## Design Choice

- **Phase 1**: planar square array for 2D direction finding.
- **Phase 2**: tetrahedral or other 3D arrangement for full localization.

The geometry directly affects localization accuracy; well-conditioned arrays reduce sensitivity to TDOA errors.