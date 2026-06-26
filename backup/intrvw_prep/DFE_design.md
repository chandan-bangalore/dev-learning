# Digital Front End (DFE) — Reference Notes & Interview Preparation

> Based on project experience: NXP VSPA DSP (LA9310) and GPP/COTS platforms
> Relevant specs: TS 38.104, TS 38.141

---

## 1. DFE Chain Overview

### TX Chain
```
IFFT → Upsampling (×4) → CFR → DPD → IQ Imbalance Correction → DAC → Mixer → [PA] → air
```

### RX Chain
```
air → ADC → Decimation (×4) → IQ Correction → FFT
```

Each block compensates for a specific real-world hardware imperfection. Without these blocks, the transmitted signal would fail 3GPP conformance tests for ACLR and EVM as defined in TS 38.141.

DFE bridges the clean digital baseband to the dirty analog world. Each block undoes or pre-compensates for one analog limitation: CFR (PA can't handle OFDM peaks), DPD (PA isn't linear), IQ/DC correction (mixers aren't perfect), upsampling (DAC sample rate ≠ baseband rate).

Upsampling matters because the DAC creates spectral images every Fs. At 30.72 Msps, the first image sits 30.72 MHz away from your signal — a brutal analog filter requirement. Push the sample rate to 245.76 Msps (8×) and the first image moves to ~215 MHz away — easy to kill with a cheap LPF.

---

## 2. Block-by-Block Explanation

---

### 2.1 Upsampling (×4) — TX / Decimation (×4) — RX

**Purpose:**
The baseband signal (post-IFFT) is at the NR channel bandwidth sample rate. Upsampling by ×4 moves it to a higher sample rate before CFR and DPD.

**Why upsampling is needed before CFR/DPD:**
CFR clips peaks and DPD pre-distorts the signal — both operations create **out-of-band spectral energy** (harmonics and intermodulation products) that extend well beyond the channel bandwidth. To observe and correct this out-of-band energy, you need a sample rate high enough to represent it — i.e., at least ×4 of the signal bandwidth. If you ran CFR/DPD at baseband rate, you would miss the adjacent channel splatter entirely.

**RX side:** Decimation is the reverse — after IQ correction at high sample rate, downsample back to baseband before the FFT.

---

### 2.2 CFR — Crest Factor Reduction

**The Problem: High PAPR in OFDM**

NR uses OFDM — a sum of many independent subcarriers. When subcarriers align in phase, their amplitudes add constructively, producing very high instantaneous peaks. The ratio of peak power to average power is called **PAPR (Peak-to-Average Power Ratio)** and can reach 10–12 dB for NR signals.

A high PAPR forces the PA to be sized for the peak, causing it to operate mostly in its inefficient linear region. Occasional peaks that exceed the PA's linear range cause **clipping distortion → spectral regrowth → ACLR violations**.

**What CFR Does:**
CFR reduces the peaks before the signal reaches the PA, targeting a PAPR of typically 8–9 dB, without significantly degrading EVM.

**CFR is a 3-step process:**

#### Step 1 — Peak Search
Scan the upsampled signal to identify samples whose amplitude exceeds the clipping threshold. The threshold is set based on the target PAPR.

#### Step 2 — Clipping
Hard-limit the identified peaks to the threshold. This reduces PAPR immediately.

**However:** Clipping in the time domain = multiplying by a rectangular window at peak locations = convolution in frequency domain → **spectral regrowth**. The clipped signal now has out-of-band emissions — the very problem CFR is trying to prevent.

#### Step 3 — FIR Filtering (15 taps)
A bandpass/low-pass FIR filter removes the out-of-band spectral splatter introduced by clipping, restoring spectral compliance.

**The catch:** Filtering in frequency = smoothing in time → **peaks partially grow back**. Not to their original height, but partially. This is why CFR is inherently iterative.

**CFR Iteration Loop:**
```
Peak Search → Clip → FIR Filter → Peak Search → Clip → FIR Filter → ...
             (repeat 3–5 times until PAPR target AND spectral mask are both met)
```

**Why 15 taps?**
Tap count controls filter roll-off sharpness:
- More taps → sharper roll-off → better out-of-band rejection → but more peak restoration (worse PAPR)
- Fewer taps → peaks restored less → but poorer spectral cleaning

15 taps is a pragmatic balance between PAPR reduction, ACLR compliance, filter latency, and cycle budget on real-time DSP hardware (VSPA).

**The fundamental CFR trade-off:**

| Action        | Effect on Peaks            | Effect on Spectrum |
|---|---|---|
| Clipping      | ↓ Reduces peaks            | ✗ Spreads energy out-of-band |
| FIR Filtering | ↑ Partially restores peaks | ✓ Cleans out-of-band emissions |

---

### 2.3 DPD — Digital Pre-Distortion

**The Problem: PA Non-Linearity**

The Power Amplifier is inherently non-linear, especially near saturation. This causes:
- **In-band distortion** → degrades EVM
- **Spectral regrowth** into adjacent channels → ACLR violations

Both are directly tested in TS 38.141.

**What DPD Does:**
DPD applies the **inverse of the PA's non-linearity** to the signal *before* it enters the PA. When the PA then distorts the pre-distorted signal, the two effects cancel, and the output is approximately linear.

```
Signal → [DPD: pre-distort] → [PA: distorts] → Linear output ✓
```

The DPD model is derived by observing the PA output via a feedback/observation path and fitting a non-linear model (generalized memory polynomial model, Volterra series) to characterize and invert its behaviour.

**Why CFR must come before DPD:**
With CFR already reducing peaks, the PA operates in a more predictable, stable region of its non-linearity. This makes the DPD model more accurate. If peaks were unconstrained, the PA would occasionally saturate in unpredictable ways that DPD cannot model reliably.

---

### 2.4 IQ Imbalance / QEC — Quadrature Error Correction

**The Problem: Analog I/Q Mismatch**

The RF front-end generates I and Q paths that are supposed to be exactly 90° apart and equal in amplitude. Due to component tolerances in the analog/RF hardware:
- Phase difference deviates from 90° → **phase imbalance**
- I and Q amplitudes differ → **amplitude imbalance**

This causes **image interference** — energy from a subcarrier leaks into its mirror subcarrier on the opposite side of DC, corrupting the constellation and degrading EVM.

**TX side (IQ Imbalance block):**
Pre-corrects the I/Q signals digitally before the DAC, so that after analog imperfections, the transmitted signal is clean.

**RX side (IQ Correction block):**
Estimates and corrects I/Q imbalance introduced by the ADC and analog RX chain, **restoring orthogonality** before the FFT processes the signal.

---

### 2.5 Block Placement Summary

| Block              | Position            | Compensates For                     | 3GPP Metric Protected |
|---|---|---|---|
| Upsampling ×4      | After IFFT          | Sample rate for wideband correction | Enables CFR/DPD accuracy |
| CFR                | After upsampling    | High PAPR of OFDM                   | ACLR, PA efficiency |
| DPD                | After CFR           | PA non-linearity                    | ACLR, EVM |
| IQ Imbalance (TX)  | Before DAC          | Analog I/Q mismatch                 | EVM, image rejection |
| IQ Correction (RX) | After ADC           | Analog I/Q mismatch                 | EVM, sensitivity |
| Decimation ×4      | After IQ correction | Return to baseband rate             | Clean baseband for FFT |

---

## 3. Interview Questions & Answers

---

### Q1: What is PAPR and why is it a problem in 5G NR?

**Answer:**
PAPR stands for Peak-to-Average Power Ratio. NR uses OFDM, which sums many independent subcarriers. When subcarriers align constructively, instantaneous amplitude can be much higher than the average — typically 10–12 dB for NR signals. This is a problem because the PA must be sized to handle the peak without clipping, meaning it operates mostly in its inefficient linear region. When peaks do exceed the PA's linear range, they cause non-linear distortion, which appears as spectral regrowth into adjacent channels (ACLR violation) and EVM degradation.

---

### Q2: What is CFR and what are its three steps?

**Answer:**
CFR (Crest Factor Reduction) reduces the PAPR of the OFDM signal before it reaches the PA. It operates in three steps:
1. **Peak search** — scan the upsampled signal to find samples exceeding the clipping threshold
2. **Clipping** — hard-limit those samples to the threshold, reducing PAPR
3. **FIR filtering** — remove the out-of-band spectral splatter introduced by clipping

These three steps are typically iterated 3–5 times because clipping creates spectral regrowth, and filtering partially restores the peaks — so a single pass is insufficient to satisfy both the PAPR target and the spectral mask simultaneously.

---

### Q3: Why do we need FIR filtering after clipping in CFR?

**Answer:**
Clipping in the time domain is equivalent to multiplying the signal by a rectangular window at the peak locations, which in the frequency domain causes convolution — spreading energy across a wide bandwidth. This spectral regrowth would cause ACLR violations. The FIR filter removes this out-of-band energy and restores spectral compliance. The trade-off is that filtering (smoothing in time) partially restores the clipped peaks, which is why CFR must iterate.

---

### Q4: Why does CFR operate at an upsampled rate (×4)?

**Answer:**
Clipping and filtering create out-of-band spectral energy that extends well beyond the channel bandwidth — into adjacent channels and beyond. To observe and correct this energy, the sample rate must be high enough to represent it. At baseband rate, you can only see energy within the channel bandwidth; you'd miss the adjacent-channel splatter that needs to be cleaned up. Operating at ×4 upsampled rate ensures CFR captures and corrects the full spectral extent of the distortion.

---

### Q5: What is DPD and how does it work?

**Answer:**
DPD (Digital Pre-Distortion) compensates for the non-linearity of the Power Amplifier. It applies the inverse of the PA's non-linear transfer function to the signal before it enters the PA. When the PA then distorts the signal, the pre-distortion and PA distortion cancel, and the output is approximately linear. The DPD model is derived by feeding a known signal through the PA, observing the output via a feedback path, and fitting a non-linear model (such as a memory polynomial or Volterra series) to characterize the PA's behaviour.

---

### Q6: Why must CFR come before DPD in the TX chain?

**Answer:**
DPD models the PA's non-linearity and applies the inverse. However, if PAPR is very high, the PA occasionally saturates in ways that are hard to model — the PA's behaviour at extreme peaks is unpredictable and can vary with temperature and operating conditions. CFR first brings the peaks into a manageable range, keeping the PA operating in a more stable, predictable region of its non-linearity. This makes the DPD model more accurate and stable. If you reversed the order, DPD would be trying to correct a highly variable, peak-driven non-linearity, which degrades its effectiveness.

---

### Q7: What is IQ imbalance and what does it cause in the frequency domain?

**Answer:**
IQ imbalance is a mismatch in the analog RF front-end between the I and Q paths — either a phase difference that deviates from 90° (phase imbalance), an amplitude difference between the two paths (amplitude imbalance), or both. In the frequency domain, IQ imbalance causes **image interference**: energy from a subcarrier at frequency +f leaks into the mirror subcarrier at frequency −f. In OFDM, this means subcarriers corrupt each other's data, degrading EVM and in severe cases causing demodulation failures.

---

### Q8: Why is IQ correction applied before the FFT on the RX side?

**Answer:**
The IQ imbalance is introduced by the analog ADC and RF RX chain — it affects the raw time-domain I/Q samples coming out of the ADC. If you waited until after the FFT to correct it, the imbalance would have already caused image interference between subcarriers in the frequency domain, making correction much more complex (you'd need to jointly process pairs of mirror subcarriers). Correcting in the time domain before the FFT is simpler and more effective — a 2×2 matrix correction per sample restores I/Q orthogonality cleanly.

---

### Q9: How do CFR and DPD relate to the TS 38.141 conformance tests?

**Answer:**
TS 38.141 defines the conformance test procedures for gNB, including transmitter tests for ACLR (Adjacent Channel Leakage Ratio) and EVM (Error Vector Magnitude). ACLR measures how much power leaks into adjacent channels — CFR and DPD are the primary mechanisms that keep this within limits. EVM measures constellation distortion — DPD and IQ imbalance correction together protect EVM. Without CFR and DPD, a real PA driving an NR waveform would almost certainly fail the ACLR test in TS 38.141. The MATLAB testbenches I developed to verify these metrics were essentially a software replica of the 38.141 test procedure.

---

### Q10: What is the relationship between PAPR, CFR, and the target ACLR value?

**Answer:**
They are tightly coupled. High PAPR forces the PA to clip at peaks, and clipping is a non-linear operation that generates intermodulation products — which appear as power in adjacent channels, i.e., degraded ACLR. CFR reduces PAPR before the PA, so the PA clips less (or not at all within its linear range), directly improving ACLR. DPD then further corrects residual non-linearity. The CFR clipping threshold is chosen as a trade-off: too aggressive (low threshold) → good PAPR but EVM degradation from over-clipping; too conservative (high threshold) → good EVM but insufficient PAPR reduction → PA still clips → ACLR fails. The target PAPR after CFR is tuned to satisfy both EVM and ACLR limits simultaneously as specified in TS 38.104/141.

---

*Generated from project experience and technical discussion — Chandan Bangalore | May 2026*
