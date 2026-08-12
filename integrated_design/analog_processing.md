# Analog Processing Chain

## Signal Chain Overview

For each channel \(i\):

```text
Mic i
  ↓
Preamplifier (TLV9062)
  ↓
Analog Recording Gate (ADG884)
  ↓
Record Driver + Bias
  ↓
Record Head (Track i)
  ↓
Tape
  ↓
Playback Head (Track i)
  ↓
Read Preamplifier (TLV9062)
  ↓
Gain Trim
  ↓
Channel i output: x_i(t)
```

All channels share:

- Single 5 V analog supply.
- Mid-rail reference \(V_\text{MID} \approx 2.5\ \text{V}\).
- Common Arduino Gate signal.

## Reference Channel and TDOA Estimation

Choose Mic 1 as reference:

```text
x_ref(t) = x_1(t)
x_i(t), i = 2,3,4
```

For each pair (1,i):

1. Apply an adjustable delay \(\tau\) to one channel.
2. Subtract:

   \[
   e_{1i}(t;\tau) = x_1(t) - x_i(t-\tau)
   \]

3. Square:

   \[
   s_{1i}(t;\tau) = e_{1i}^2(t;\tau)
   \]

4. Integrate over the frame:

   \[
   E_{1i}(\tau) = \int_{\text{frame}} s_{1i}(t;\tau)\,dt
   \]

5. Find \(\hat{\tau}_{1i}\) that minimizes \(E_{1i}(\tau)\).

## Delay Implementation Options

### Mechanical Delay

- Fix the reference playback head.
- Mount the other playback heads on micrometer stages.
- Adjust physical positions to change \(\tau\).

Advantages:

- Purely analog.
- No additional active components in the signal path.

Disadvantages:

- Manual adjustment.
- Limited dynamic range.

### Electronic Delay

Use analog delay lines (e.g., BBD or dedicated delay ICs) to implement \(\tau\) electronically.

Advantages:

- Programmable.
- Suitable for automated search.

Disadvantages:

- Added noise and distortion.
- Sampling artifacts in BBDs.

Initial design: mechanical delay for proof of concept; electronic delay reserved for advanced versions.

## Subtractor

Use a matched-resistor difference amplifier (TLV9062):

\[
V_\text{out} = \frac{R_f}{R_\text{in}}(V_1 - V_2)
\]

Initial gain:

```text
R_f = R_in = 10 kΩ → G = 1
```

Use 0.1% resistors or a matched network for high common-mode rejection.

## Squarer

Preferred component:

```text
ADL5391
```

Configured as a multiplier with both inputs tied together:

\[
V_\text{out} \propto V_\text{in}^2
\]

ADL5391 operates from 4.5 to 5.5 V and has wide bandwidth, making it suitable for accurate analog squaring.

## Integrator

Op-amp integrator (TLV9062):

- Input resistor \(R_\text{int}\).
- Feedback capacitor \(C_\text{int}\).
- Parallel discharge resistor \(R_\text{leak}\).

Time constant:

\[
\tau_\text{int} = R_\text{leak} C_\text{int}
\]

The integration window is synchronized with the audio frame.

## Sample and Hold

At the end of each frame:

```text
Integrator output → Analog switch → Hold capacitor → Buffer
```

Arduino generates a short `SAMPLE_PULSE` to capture the energy value for each \(\tau\) setting.

## Output

For each pair (1,i):

```text
E_1i(τ) as a function of τ
Minimum → τ̂_1i
```

These TDOA estimates are then used in the localization model.