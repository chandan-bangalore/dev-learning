# Interpolation & Decimation (5G NR) – Summary Notes

## System Context
- FFT size: 512 → 2048 → 512
- Sampling rates:
  - Fs₀ = 7.68 MHz
  - Fs₁ = 15.36 MHz
  - Fs₂ = 30.72 MHz
- Bandwidth:
  - 25 RB → 300 subcarriers
  - Occupied BW = 4.5 MHz
  - Passband edge = 2.25 MHz
  - Stopband edge ≈ 2.5 MHz

---

## 1. Filters

### Low Pass Filter (LPF)
Passes low frequencies and attenuates high frequencies.

Use cases:
- Remove images (after interpolation)
- Prevent aliasing (before decimation)

---

### FIR Filter
Finite Impulse Response filter:

```
y[n] = Σ h[k] x[n-k]
```

Properties:
- Always stable
- Can be linear phase
- Hardware friendly

---

### firpm (Parks–McClellan)
- Equiripple (minimizes huge ripples at passband/stopband) optimal FIR design
- Minimizes maximum error

---

### Filter Characteristics
- Passband
- Stopband
- Transition band
- Ripple (passband & stopband)
- Stopband attenuation
- Number of taps (complexity)

---

### Choosing Number of Taps

Trade-off:
- Narrow transition → more taps
- More attenuation → more taps

Hardware constraint (example):
- 15 MACs per cycle → choose 15 taps

---

## 2. Images & Aliasing

Interpolation = stretching time → creates copies in frequency
Decimation = compressing time → causes overlap in frequency

### Images (Interpolation) : useful band signal is compressed
- Created due to zero insertion
- Spectrum gets repeated

Fix:
- LPF after interpolation (keeps signal, removes high frequency components i.e images)

---

### Aliasing (Decimation)
- High-frequency content folds into baseband

Fix:
- LPF before decimation (keeps signal, removes high frequency components i.e aliased part)

---

### Key Insight
- Images are removable
- Aliasing is irreversible

---

## 3. Polyphase Implementation

### Concept
Split FIR filter into phases for efficient computation.

### Benefits
- Avoids zero multiplications
- Lower complexity
- Efficient for hardware (VSPA)

### Multistage Design
Instead of ×4:
- Use ×2 → ×2

Benefits:
- Smaller filters
- Better efficiency

---

## 4. Octave Testbench

```octave
clear; close all; clc;
pkg load signal;

Fs0 = 7.68e6;
Fs1 = 15.36e6;
Fs2 = 30.72e6;

fp  = 2.25e6;
fsb = 2.50e6;

function h = design_lpf(Fs, fp, fsb, Ntaps)
    nyq = Fs/2;
    h = firpm(Ntaps-1, [0 fp fsb nyq]/nyq, [1 1 0 0]);
    h = h / sum(h);
end

h1 = design_lpf(Fs1, fp, fsb, 31);
h2 = design_lpf(Fs2, fp, fsb, 15);

h1i = 2*h1; h2i = 2*h2;

x = randn(7680,1) + 1j*randn(7680,1);

% Interpolation
y1 = upsample(x,2);
y1 = conv(y1,h1i);
y2 = upsample(y1,2);
y2 = conv(y2,h2i);

% Decimation
z1 = conv(y2,h2);
z1 = z1(1:2:end);
z2 = conv(z1,h1);
z2 = z2(1:2:end);
```

---

## 5. Interview Questions & Answers

### Q1: What is aliasing?
Aliasing is frequency overlap due to insufficient sampling, causing distortion.

---

### Q2: What are images?
Spectral replicas created during interpolation due to zero insertion.

---

### Q3: Why filter before decimation?
To remove high-frequency components that would alias.

---

### Q4: Why filter after interpolation?
To remove spectral images.

---

### Q5: FIR vs IIR?
- FIR: stable, linear phase
- IIR: efficient but nonlinear phase

---

### Q6: What is polyphase?
Rewriting filters into multiple phases for efficient multirate processing.

---

### Q7: Why multistage interpolation?
Reduces filter complexity and improves efficiency.

---

### Q8: What determines number of taps?
Transition bandwidth and required attenuation.

---

### Q9: Is aliasing reversible?
No.

---

### Q10: Why linear phase important in OFDM?
Prevents distortion across subcarriers. Otherwise I guess it loses orthogonality b/w subcarriers - not sure.

---

### Q11: What happens if the transition band shrinks?
Shrinking the transition band makes the filter sharper, which requires more taps (higher order), increasing complexity and latency.

---

### Q12: How do you reduce ripple in a filter?
Ripple can be reduced by increasing the number of taps, adjusting design weights (in equiripple design), or widening the transition band.

---

### Q13: Why use windowing vs equiripple (firpm)?
Windowing is simple and fast but not optimal, while equiripple (firpm) provides optimal performance with better control over ripple and transition sharpness.

---

### Q14: Why does upsampling create images?
Upsampling inserts zeros, which causes periodic replication of the spectrum in the frequency domain, creating images.

---

### Q15: Why does downsampling cause aliasing?
Downsampling reduces the sampling rate, compressing the spectrum and causing different frequency components to overlap (alias).

---

### Q16: Is aliasing reversible?
No, aliasing is irreversible because different frequency components overlap and cannot be separated.

---

### Q17: Are images reversible?
Yes, images can be removed using a low-pass filter after interpolation.

---

### Q18: Why is linear phase important in OFDM systems?
Linear phase ensures all frequency components experience the same delay, preventing distortion of subcarriers and preserving signal integrity.

---

### Q19: What determines the number of taps in a filter?
The number of taps is determined by transition bandwidth, required attenuation, and allowable ripple.

---

### Q20: Why use multistage interpolation/decimation?
Multistage design reduces filter complexity, improves efficiency, and allows shorter filters at each stage.

---

## Final Takeaway
- Interpolation creates images → remove using LPF
- Decimation causes aliasing → prevent using LPF
- Polyphase + multistage → efficient hardware implementation

