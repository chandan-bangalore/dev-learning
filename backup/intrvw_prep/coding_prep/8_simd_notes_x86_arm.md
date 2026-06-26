# Section I — SIMD Literacy (AVX2 + ARM NEON) Study Notes

How nr_ue_phy uses SIMD intrinsics, and enough background that you can read AVX2 and
NEON code in the codebase (and in an interview) without freezing up.

The advice from the original roadmap stands: **don't try to write SIMD from scratch.
Read it.** You'll write it once a year, you'll read it weekly. Aim for *literacy*, not
fluency.

For each topic:
1. **Layman** — what it actually is, in plain English
2. **In this project** — how nr_ue_phy uses it
3. **Minimal example** — a tiny self-contained snippet
4. **In tree** — concrete `file:line` pointer into nr_ue_phy

---

## Table of contents

- [I0. Why SIMD at all](#i0-why-simd-at-all)
- [I1. AVX2 basics — vectors, intrinsics, naming](#i1-avx2-basics--vectors-intrinsics-naming)
- [I2. NEON basics — vectors, intrinsics, naming](#i2-neon-basics--vectors-intrinsics-naming)
- [I3. Reading the names — the cheat sheet](#i3-reading-the-names--the-cheat-sheet)
- [I4. Saturating vs wrap-around arithmetic](#i4-saturating-vs-wrap-around-arithmetic)
- [I5. Why SIMD lives only in lib/x86 and lib/platform](#i5-why-simd-lives-only-in-libx86-and-libplatform)
- [I6. Walkthrough — AVX2 BPSK demodulator](#i6-walkthrough--avx2-bpsk-demodulator)
- [I7. Walkthrough — AVX2 descrambler](#i7-walkthrough--avx2-descrambler)
- [I8. Walkthrough — NEON QPSK demodulator](#i8-walkthrough--neon-qpsk-demodulator)
- [I9. Interview-ready talking points](#i9-interview-ready-talking-points)

---

## I0. Why SIMD at all

**Layman.** SIMD = "Single Instruction, Multiple Data." A normal CPU instruction adds
two 32-bit numbers in one cycle. A SIMD instruction adds *eight* 32-bit numbers (or
sixteen 16-bit, or thirty-two 8-bit) in roughly the same cycle. For loops where the
operation is identical for every element — exactly what DSP does — this is a 4-32×
speed-up before the CPU even tries to be clever about pipelining.

**Cost.** You give up:
- **Portability.** AVX2 code doesn't run on ARM; NEON code doesn't run on x86.
- **Readability.** `_mm256_packs_epi32(_mm256_srai_epi32(x, 13), zero)` is not obvious.
- **Branching.** Inside a SIMD loop you can't `if (this_lane) { ... }` — you have to
  compute both branches and blend the results with a mask.

For a PHY processing a 1 ms slot at 30.72 MS/s, the speedup is non-negotiable. So we pay.

**In this project.** All inner-loop math (FFT, equalization, demodulation, descrambling,
CRC, scrambler PRBS) has a SIMD implementation: AVX2 for x86 builds, NEON for ARM
production builds. Scalar fallbacks exist for tail cases (when `num_symbols` isn't a
multiple of the vector width).

---

## I1. AVX2 basics — vectors, intrinsics, naming

**Layman.** Intel's AVX2 gives you 256-bit vector registers (`%ymm0`..`%ymm15`). A
256-bit register holds:

| Type | Lanes |
|---|---|
| 32× `int8_t` / `uint8_t` | `__m256i` |
| 16× `int16_t` / `uint16_t` | `__m256i` |
| 8× `int32_t` / `float` | `__m256i` / `__m256` |
| 4× `int64_t` / `double` | `__m256i` / `__m256d` |

You don't write asm — you call **intrinsics**, which are `inline` C functions that compile
to one instruction. They live in `<immintrin.h>`. They look like:

```
_mm256_<op>_<type>     e.g. _mm256_add_epi16  (add 16× int16)
_mm256_<op>_<type>     e.g. _mm256_loadu_si256 (load 32 bytes, unaligned)
```

**Type naming.**
- `epiN` = packed signed integer of N bits (`epi8`, `epi16`, `epi32`, `epi64`)
- `epuN` = packed *unsigned* integer
- `ps` / `pd` = packed single / double precision float
- `si256` = "the whole 256-bit integer register"

**The five operations you'll see most.**
- `_mm256_set1_epi16(x)` — broadcast `x` into all 16 lanes (a "splat")
- `_mm256_loadu_si256(p)` — load 32 bytes from `p` (unaligned)
- `_mm256_storeu_si256(p, v)` — store 32 bytes to `p` (unaligned)
- `_mm256_add_epi16(a, b)` — lane-wise add
- `_mm256_madd_epi16(a, b)` — multiply paired int16s, sum adjacent → int32 (the workhorse
  for complex multiplication)

**Reference.** The Intel Intrinsics Guide
(<https://www.intel.com/content/www/us/en/docs/intrinsics-guide/index.html>) is *the*
documentation. Type any intrinsic into the search; it shows you the C semantics and the
underlying instruction. Bookmark it.

**Minimal example.**
```c
#include <immintrin.h>
#include <stdio.h>

int main(void) {
    int16_t a[16] = { 1,2,3,4,5,6,7,8, 9,10,11,12,13,14,15,16 };
    int16_t b[16] = { 10,10,10,10,10,10,10,10, 10,10,10,10,10,10,10,10 };
    int16_t out[16];

    __m256i va = _mm256_loadu_si256((__m256i_u *)a);
    __m256i vb = _mm256_loadu_si256((__m256i_u *)b);
    __m256i vc = _mm256_add_epi16(va, vb);
    _mm256_storeu_si256((__m256i_u *)out, vc);

    for (int i = 0; i < 16; i++) printf("%d ", out[i]);
    /* prints: 11 12 13 ... 26 */
}
/* compile: gcc -mavx2 -O2 ex.c -o ex */
```
Note `-mavx2` — the compiler refuses to emit AVX2 instructions otherwise.

**In tree.**
- The PHY's AVX2 source root: [lib/x86/](/home/cb24/workspace/nr_ue_phy/lib/x86/)
- An especially clean entry point — the BPSK demodulator's vector loop:
  [lib/x86/cn_demodulator.c:117](/home/cb24/workspace/nr_ue_phy/lib/x86/cn_demodulator.c#L117)

---

## I2. NEON basics — vectors, intrinsics, naming

**Layman.** ARM's NEON is the ARM equivalent of AVX2 with smaller registers — 128-bit
(`%v0`..`%v31`). A 128-bit register holds:

| Type | Lanes |
|---|---|
| 16× `int8_t` / `uint8_t` | `int8x16_t` / `uint8x16_t` |
| 8× `int16_t` / `uint16_t` | `int16x8_t` / `uint16x8_t` |
| 4× `int32_t` / `float` | `int32x4_t` / `float32x4_t` |
| 2× `int64_t` / `double` | `int64x2_t` / `float64x2_t` |

NEON intrinsics live in `<arm_neon.h>`. The naming convention is regular:

```
v<op>q_<type>          q = "quadword" = 128-bit (omit q for 64-bit half-vectors)

vaddq_s16              add, quadword, signed-16-bit
vld1q_s16              load,  quadword, signed-16-bit
vst1q_s8               store, quadword, signed-8-bit
vdupq_n_s16            duplicate scalar n into all 8 lanes (= AVX's set1)
vqrdmulhq_s16          saturating rounding doubling multiply, high half (Q15 multiply!)
```

**The cluster you'll see most in this project.**

| Intrinsic | What it does |
|---|---|
| `vld1q_s16(p)` | Load 8 int16 from `p` |
| `vst1q_s16(p, v)` | Store 8 int16 to `p` |
| `vdupq_n_s16(x)` | Broadcast scalar `x` to all 8 lanes |
| `vaddq_s16(a, b)` | Lane-wise add |
| `vmulq_s16(a, b)` | Lane-wise low-half multiply |
| `vqrdmulhq_s16(a, b)` | Lane-wise **Q15** multiply (`(a*b + (1<<14)) >> 15`, saturated) |
| `vminq_s16` / `vmaxq_s16` | Lane-wise min / max — used for saturation/clamping |
| `vshrq_n_s16(a, k)` | Lane-wise arithmetic right-shift by compile-time `k` |
| `vqmovn_s16(a)` | Saturating narrow: 8× int16 → 8× int8 |

**Where each name part comes from.**
- `v` — vector
- `q` — full 128-bit (quadword) register
- the op (`add`, `mul`, `ld1`, etc.)
- the type (`s16` = signed 16-bit, `u8` = unsigned 8-bit, etc.)

**Minimal example.**
```c
#include <arm_neon.h>
#include <stdio.h>

int main(void) {
    int16_t a[8] = { 1, 2, 3, 4, 5, 6, 7, 8 };
    int16_t b[8] = { 10, 10, 10, 10, 10, 10, 10, 10 };
    int16_t out[8];

    int16x8_t va = vld1q_s16(a);
    int16x8_t vb = vld1q_s16(b);
    int16x8_t vc = vaddq_s16(va, vb);
    vst1q_s16(out, vc);

    for (int i = 0; i < 8; i++) printf("%d ", out[i]);
    /* prints: 11 12 13 14 15 16 17 18 */
}
```
On your RPi (which is ARMv8): `gcc -O2 ex.c -o ex` — NEON is on by default for AArch64.

**Reference.** ARM's intrinsics reference
(<https://developer.arm.com/architectures/instruction-sets/intrinsics/>). Same role as
the Intel guide.

**In tree.**
- The PHY's NEON source root:
  [lib/platform/arm_ran/](/home/cb24/workspace/nr_ue_phy/lib/platform/arm_ran/)
- Clean entry — the QPSK demodulator's vector loop:
  [lib/platform/arm_ran/nr.c:360](/home/cb24/workspace/nr_ue_phy/lib/platform/arm_ran/nr.c#L360)

---

## I3. Reading the names — the cheat sheet

You don't need to memorise every intrinsic. You need to **decode names on sight.**

### AVX2

```
_mm256_<verb>_<type>
_mm<width>_<verb>_<type>     where width is 128 or 256

_mm256_add_epi16             add 16 lanes of int16
_mm256_madd_epi16            multiply pairs of int16, sum into int32 (8 results)
_mm256_packs_epi32           saturate-pack 8+8 int32s → 16 int16
_mm256_packs_epi16           saturate-pack 16+16 int16s → 32 int8
_mm256_srai_epi32            shift-right arithmetic immediate, 32-bit lanes
_mm256_shuffle_epi8          byte-wise shuffle within 128-bit halves (per-byte permute)
_mm256_blendv_epi8           pick byte from a or b based on top bit of mask
_mm256_cmpeq_epi8            lane-wise equality, returns 0xFF (true) or 0x00 (false)
_mm256_min_epi8 / max_epi8   lane-wise min / max — your clamp instructions
_mm256_sign_epi8(a, b)       multiply each byte of a by sign(b) — handy for ±1
_mm256_set1_epiN             broadcast scalar
_mm256_setzero_si256         all zeros
_mm256_loadu_si256           unaligned 256-bit load
_mm256_storeu_si256          unaligned 256-bit store
```

### NEON

```
v<verb>q_<type>              q = 128-bit; drop q for 64-bit half-vector
                             prefix v… (sometimes vqsomething for "saturating")

vaddq_s16                    add (wrap on overflow)
vqaddq_s16                   add (saturate on overflow)
vmulq_s16                    multiply (low half)
vqrdmulhq_s16                Q15 saturating-rounding-multiply, high half
vminq_s16  / vmaxq_s16       lane-wise min / max
vshrq_n_s16                  shift right by compile-time const
vqmovn_s16                   saturating narrow 16→8 (output = half-vector)
vcombine_s8                  combine two 64-bit half-vectors → one 128-bit
vld1q_s16  / vst1q_s16       load / store 128 bits
vdupq_n_s16                  splat scalar
vld2q_s16                    de-interleave load (loads 16 int16, returns {even, odd})
vbslq_s8                     bit-select (= blend) by mask
```

When you see something unfamiliar, parse the name part-by-part — `vqrdmulhq_s16` =
"vector, **q**uadword, **r**ounding, **d**oubling, **mul**tiply, **h**igh-half, **s16**".

---

## I4. Saturating vs wrap-around arithmetic

**Layman.** Two ways to handle integer overflow:
- **Wrap** — `127 + 1 = -128` (two's complement rollover). Default in C and in plain
  intrinsics like `_mm256_add_epi8` / `vaddq_s8`.
- **Saturate** — `127 + 1 = 127` (clamp to the max representable value). What you almost
  always want in DSP, where overflow produces visually obvious garbage in the output.

In SIMD intrinsics, "saturating" is signalled by:
- AVX2: `_mm256_adds_epi8` / `_mm256_subs_epi8` / `_mm256_packs_*` (the `s` and `packs`)
- NEON: a `q` prefix on the verb — `vqaddq`, `vqsubq`, `vqmovn` (the "**q**uery" / saturating)

**In this project.** Demodulator outputs (LLRs) are 8-bit signed, so values must clamp
into `[MIN_LLR, MAX_LLR]`. The PHY uses saturating ops at the narrow point of every
pipeline (`_mm256_packs_epi16` to go 16→8, `vqmovn_s16` likewise). You'll also see
explicit `min`/`max` clamps to project-specific ranges (`max_range`, `min_range`).

**Minimal example.**
```c
/* AVX2 — saturating add of int8 */
__m256i a = _mm256_set1_epi8(120);
__m256i b = _mm256_set1_epi8(20);
__m256i c = _mm256_adds_epi8(a, b);   /* every lane = 127, not -116 */
```

```c
/* NEON — saturating narrow 16 → 8 */
int16x8_t v = vdupq_n_s16(500);       /* > 127, will saturate */
int8x8_t  o = vqmovn_s16(v);          /* every lane = 127 */
```

**In tree.**
- AVX2 saturating narrow used to produce 8-bit LLRs from int16:
  [lib/x86/cn_demodulator.c:142-145](/home/cb24/workspace/nr_ue_phy/lib/x86/cn_demodulator.c#L142-L145)
- NEON saturating narrow at the same step:
  [lib/platform/arm_ran/nr.c:376](/home/cb24/workspace/nr_ue_phy/lib/platform/arm_ran/nr.c#L376)

---

## I5. Why SIMD lives only in lib/x86 and lib/platform

**Layman.** Project rule: `src/` is platform-independent. SIMD intrinsics are inherently
platform-specific. Therefore SIMD lives behind the `cn_*` API in `lib/x86/` (the AVX2
implementation) and `lib/platform/arm_ran/` (the NEON implementation). At build time,
the right one is linked based on the target.

This is a deliberate engineering trade-off:
- `src/` stays portable, easy to read, easy to test on a laptop
- The hard, fast paths are isolated; if you change the math, you update both `lib/x86/`
  and `lib/platform/arm_ran/` in the same commit
- A scalar reference exists too, used as a fallback for tail handling and as a sanity
  check during testing

**In this project.** The same function (`cn_demod_qpsk`, `cn_descramble`, etc.) has:
- A header in `lib/cn/inc/` declaring the API
- An AVX2 implementation in `lib/x86/cn_xxx.c`
- A NEON implementation in `lib/platform/arm_ran/nr.c`
- A scalar fallback (often a `static` in the AVX2 file) used for the trailing elements
  outside the SIMD block size

This is the dispatcher pattern referenced from
[CLAUDE.md → src/CLAUDE.md](/home/cb24/workspace/nr_ue_phy/src/CLAUDE.md). If you ever
catch a SIMD intrinsic in `src/`, that's a review-blocker.

**In tree.**
- AVX2 + scalar fallback in one file (BPSK):
  [lib/x86/cn_demodulator.c:117](/home/cb24/workspace/nr_ue_phy/lib/x86/cn_demodulator.c#L117)
- NEON in another file, same API contract:
  [lib/platform/arm_ran/nr.c:334](/home/cb24/workspace/nr_ue_phy/lib/platform/arm_ran/nr.c#L334)

---

## I6. Walkthrough — AVX2 BPSK demodulator

This is the cleanest AVX2 example in the codebase. Read it line-by-line.

**The math.** BPSK soft demod = "scale the real part of each symbol by a noise-dependent
factor, clamp to ±max_range, output as 8-bit LLR." For 32 input symbols (each `int16` I +
`int16` Q = 4 bytes), you produce 32 output LLRs (each 1 byte).

**The code** ([lib/x86/cn_demodulator.c:117-156](/home/cb24/workspace/nr_ue_phy/lib/x86/cn_demodulator.c#L117-L156)):

```c
const __m256i v_common_factor = _mm256_set1_epi16(common_factor);    /* (1) */

for (size_t i = 0; i < num_blocks; i++, soft_bits += 32, symbols += 32) {
    /* (2) load 32 complex int16 symbols = 128 bytes = 4× __m256i */
    __m256i s0 = _mm256_loadu_si256((__m256i_u *)(symbols + 0));
    __m256i s1 = _mm256_loadu_si256((__m256i_u *)(symbols + 8));
    __m256i s2 = _mm256_loadu_si256((__m256i_u *)(symbols + 16));
    __m256i s3 = _mm256_loadu_si256((__m256i_u *)(symbols + 24));

    /* (3) madd_epi16 = take adjacent int16 pairs, multiply, sum → int32.
           For BPSK, a single madd combines (I, Q) with (factor, 0)
           or (factor, factor) shapes to extract the real part scaled. */
    __m256i x0 = _mm256_madd_epi16(s0, v_common_factor);
    __m256i x1 = _mm256_madd_epi16(s1, v_common_factor);
    __m256i x2 = _mm256_madd_epi16(s2, v_common_factor);
    __m256i x3 = _mm256_madd_epi16(s3, v_common_factor);

    /* (4) right-shift 32-bit lanes to undo the Q-format gain we just applied */
    x0 = _mm256_srai_epi32(x0, INPUT_FORMAT + OUTPUT_SHIFT);
    /* ... same for x1, x2, x3 */

    /* (5) saturating-pack int32 → int16. 4× int32 vectors → 2× int16 vectors */
    __m256i y0 = _mm256_packs_epi32(x0, x1);
    __m256i y1 = _mm256_packs_epi32(x2, x3);

    /* (6) saturating-pack int16 → int8. 2× int16 vectors → 1× int8 vector */
    __m256i t = _mm256_packs_epi16(y0, y1);

    /* (7) the packs ops shuffle 128-bit halves; we re-order to fix it */
    t = _mm256_permute4x64_epi64(t, _MM_SHUFFLE(3, 1, 2, 0));
    t = _mm256_shuffle_epi32(t, _MM_SHUFFLE(3, 1, 2, 0));

    /* (8) explicit clamp to [min_range, max_range] (already saturated to int8) */
    t = _mm256_min_epi8(t, _mm256_set1_epi8(max_range));
    t = _mm256_max_epi8(t, _mm256_set1_epi8(min_range));

    _mm256_storeu_si256((__m256i_u *)(soft_bits), t);                /* (9) */
}

/* (10) scalar fallback for elements that didn't fit into a 32-block */
_demod_bpsk(soft_bits, max_range, min_range, symbols,
            num_symbols - 32 * num_blocks, noise_power);
```

**What to notice.**
- The whole inner loop is **branch-free** (steps 2–9 do the same thing for every block).
- Steps 5+6 form a **pyramid narrowing** int32 → int16 → int8 with saturation at every
  level — this is the canonical SIMD "produce smaller output type" pattern.
- Step 7 is the price of `packs` instructions: AVX2 evaluates them per-128-bit-lane, so
  the bytes come out interleaved and you fix it with permutes.
- Step 10 — scalar tail. A SIMD function is *always* paired with a scalar tail because
  `num_symbols` is rarely a perfect multiple of 32.

---

## I7. Walkthrough — AVX2 descrambler

This one shows mask-based conditional logic: how SIMD does `if (b) negate; else keep`.

**The math.** Descramble = multiply each soft bit by `(1 - 2*b)` where `b` is the next bit
of a PRBS sequence. Equivalent: keep the LLR if `b==0`, negate if `b==1`.

**The code** ([lib/x86/cn_descrambler.c:29-57](/home/cb24/workspace/nr_ue_phy/lib/x86/cn_descrambler.c#L29-L57)):

```c
const __m256i mask1 = _mm256_set_epi8(/* ... 0x03 ×8, 0x02 ×8, 0x01 ×8, 0x00 ×8 */);
const __m256i mask2 = _mm256_set_epi8(/* ... 0x80, 0x40, 0x20, 0x10, ... 0x01 — repeated 4× */);
const __m256i plus_ones  = _mm256_set1_epi8(1);
const __m256i minus_ones = _mm256_set1_epi8(-1);

for (size_t i = 0; i < num_blocks; i++, soft_bits_out += 32, soft_bits_in += 32, prs += 4) {
    __m256i x = _mm256_loadu_si256((__m256i_u *)soft_bits_in);   /* (1) load 32 LLRs */

    memcpy(&tmp, prs, sizeof(tmp));                              /* (2) read 4 PRBS bytes (= 32 bits) */
    __m256i y = _mm256_set1_epi32(tmp);                          /*     broadcast into 8 int32 lanes */
    __m256i z = _mm256_shuffle_epi8(y, mask1);                   /* (3) "byte 0,0,0,0,0,0,0,0,1,1,1,…" */
    __m256i m = _mm256_cmpeq_epi8(_mm256_and_si256(z, mask2), mask2);  /* (4) extract each bit → 0xFF / 0x00 */
    __m256i t = _mm256_blendv_epi8(plus_ones, minus_ones, m);    /* (5) ±1 from mask */

    __m256i input_sat = _mm256_max_epi8(llr_min, _mm256_min_epi8(llr_max, x));   /* (6) clamp */
    x = _mm256_sign_epi8(input_sat, t);                          /* (7) multiply each byte by ±1 */

    _mm256_storeu_si256((__m256i_u *)soft_bits_out, x);          /* (8) store */
}
```

**What's clever.**
- Steps 2–4 are how you turn 32 packed bits into 32 bytes of `0xFF` / `0x00`:
  - Broadcast 4 bytes everywhere
  - `shuffle_epi8` makes byte i contain "the byte that holds bit i" (0,0,0,0,0,0,0,0, 1,1,…)
  - AND with `mask2` (which has only one bit set per byte) isolates the i-th bit
  - `cmpeq` produces `0xFF` if the bit was set, `0x00` if not
- Step 5 turns the 0xFF/0x00 mask into ±1 with `blendv_epi8` (per-byte conditional select).
- Step 7 — `_mm256_sign_epi8(a, b)` is a cute one-instruction "multiply byte by sign of b."
  Reading `a * sign(b)`: if `b > 0` keep `a`, if `b < 0` negate, if `b == 0` zero.

**Interview anchor.** "How do you do conditional logic in SIMD?" Answer: you don't branch
— you compute the condition as a mask of `0xFF`/`0x00`, then blend two pre-computed
results. Cite this descrambler.

---

## I8. Walkthrough — NEON QPSK demodulator

The NEON equivalent of I6, with a per-subcarrier scaling twist.

**The math.** QPSK soft demod with per-SC channel-quality weighting. For each of 8 input
complex symbols (16 int16 = re,im,re,im,…) plus 8 channel-quality scalings, produce 16
output LLRs (1 byte each).

**The code** ([lib/platform/arm_ran/nr.c:343-377](/home/cb24/workspace/nr_ue_phy/lib/platform/arm_ran/nr.c#L343-L377)):

```c
const int16x8_t cf_global = vdupq_n_s16((int16_t)common_factor);    /* (1) splat */
const int16x8_t rng_hi    = vdupq_n_s16((int16_t)range);
const int16x8_t rng_lo    = vnegq_s16(rng_hi);
const uint16x8_t q13_u    = vdupq_n_u16(SCALING_CAP_NEON);

for (; i + 16 <= n; i += 16) {
    /* (2) load 8 unsigned channel-quality scalings */
    uint16x8_t scl     = vld1q_u16(&scaling[i / 2]);

    /* (3) clamp to Q13 and reinterpret as signed (no instruction, just type pun) */
    int16x8_t scl_cap  = vreinterpretq_s16_u16(vminq_u16(scl, q13_u));

    /* (4) per-SC factor: (cf_global * scl_cap) in Q15, then <<2 to land in Q13 */
    int16x8_t cf_sc    = vqshlq_n_s16(vqrdmulhq_s16(scl_cap, cf_global), 2);

    /* (5) un-zip cf_sc so each scaling is duplicated for I and Q of its symbol:
           cf_sc = [a b c d e f g h]
           cf0   = [a a b b c c d d]   (for the 8 int16s of the first 4 symbols)
           cf1   = [e e f f g g h h]   */
    int16x4_t lo4 = vget_low_s16(cf_sc);
    int16x4_t hi4 = vget_high_s16(cf_sc);
    int16x4x2_t zlo = vzip_s16(lo4, lo4);
    int16x4x2_t zhi = vzip_s16(hi4, hi4);
    int16x8_t cf0 = vcombine_s16(zlo.val[0], zlo.val[1]);
    int16x8_t cf1 = vcombine_s16(zhi.val[0], zhi.val[1]);

    /* (6) load 16 int16s of (re,im,re,im,…) */
    int16x8_t v0 = vld1q_s16(&src[i]);
    int16x8_t v1 = vld1q_s16(&src[i + 8]);

    /* (7) Q15 multiply, right-shift to Q-out, clamp to ±range */
    v0 = vminq_s16(vmaxq_s16(vshrq_n_s16(vqrdmulhq_s16(v0, cf0), FINAL_SHIFT_NEON), rng_lo), rng_hi);
    v1 = vminq_s16(vmaxq_s16(vshrq_n_s16(vqrdmulhq_s16(v1, cf1), FINAL_SHIFT_NEON), rng_lo), rng_hi);

    /* (8) saturating narrow 16→8, combine the two halves into one 16-byte vector */
    vst1q_s8(&p_dst[i], vcombine_s8(vqmovn_s16(v0), vqmovn_s16(v1)));
}

/* scalar tail follows for i not on the 16-int16 boundary */
```

**What to notice.**
- `vqrdmulhq_s16` is the NEON "do a Q15 multiplication" workhorse — equivalent to
  `(a*b + (1<<14)) >> 15` with saturation. Read it as "fixed-point multiply." This is
  the **single most important NEON intrinsic to recognize** in DSP code.
- Step 5 (the un-zip / duplicate) is the kind of bookkeeping that makes SIMD code dense.
  You always end up with at least one "rearrange the lanes so the math lines up" block.
- Step 7 chains 4 intrinsics into one fused expression; this is normal and the compiler
  handles it. Don't refactor it for readability — the project convention is to write the
  pipeline inline.

**Interview anchor.** "What's `vqrdmulhq_s16`?" — say:
> "It's the NEON instruction for Q15 fixed-point multiplication with saturation —
> (a×b + (1<<14)) >> 15, clamped. It's the building block of fixed-point DSP on ARM."

---

## I9. Interview-ready talking points

If a SIMD question comes up, these are the things you actually want to be able to say.

**1. "Walk me through how a demodulator gets vectorized."**
> "The scalar version processes one complex symbol at a time. The vector version loads
> 8 (NEON) or 32 (AVX2) symbols in one instruction, multiplies all of them by a common
> factor in fixed-point, narrows the result with saturation, clamps to a soft-bit range,
> and stores 8 or 32 output bytes. The same code path handles every iteration — there's
> no branching inside the loop. A scalar tail handles symbols that don't fit a multiple
> of the SIMD width." Cite [lib/x86/cn_demodulator.c:117](/home/cb24/workspace/nr_ue_phy/lib/x86/cn_demodulator.c#L117)
> or [lib/platform/arm_ran/nr.c:360](/home/cb24/workspace/nr_ue_phy/lib/platform/arm_ran/nr.c#L360).

**2. "How do you do an `if` inside SIMD?"**
> "You don't branch. You compute the condition as a per-lane mask of `0xFF` or `0x00`,
> compute both possible results, then blend with `_mm256_blendv_epi8` (AVX2) or
> `vbslq_*` (NEON). The descrambler is a clean example — turning a single PRBS bit
> into ±1 in every lane uses `cmpeq` + `blendv`." Cite
> [lib/x86/cn_descrambler.c:47-48](/home/cb24/workspace/nr_ue_phy/lib/x86/cn_descrambler.c#L47-L48).

**3. "What's the difference between AVX2 and NEON?"**
> "Same idea, different vector widths. AVX2 has 256-bit vectors (32 int8 lanes); NEON has
> 128-bit (16 int8 lanes). AVX2 has more horizontal/permute ops because of its split
> 128-bit-half architecture; NEON is more orthogonal but smaller. The intrinsic naming
> is wildly different but the abstractions map: `_mm256_set1` ↔ `vdupq_n`,
> `_mm256_loadu_si256` ↔ `vld1q_s16`, `_mm256_packs_epi16` ↔ `vqmovn_s16` + `vcombine_s8`."

**4. "What's saturating arithmetic and why does DSP need it?"**
> "Wrap-around overflow turns `127 + 1` into `-128`, which produces audible/visible
> garbage in DSP outputs (a sample suddenly flips polarity). Saturation clamps to the
> max representable value instead. AVX2 saturating ops are signalled by `s` —
> `adds`, `packs`. NEON saturating ops are signalled by `q` — `vqadd`, `vqmovn`. The
> demodulator's narrowing pyramid `int32 → int16 → int8` saturates at every step." Cite
> the `packs_epi32` / `packs_epi16` chain in
> [lib/x86/cn_demodulator.c:142-145](/home/cb24/workspace/nr_ue_phy/lib/x86/cn_demodulator.c#L142-L145).

**5. "What's Q-format fixed point?"**
> "It's how you store fractional numbers in integers without using float. `Q15` means
> 'a 16-bit integer where the value represents a number in [-1, 1) scaled by 2^15.'
> Multiplying two Q15 numbers gives a 32-bit result that needs >>15 to be Q15 again. NEON
> has `vqrdmulhq_s16` which does exactly that — a saturating, rounding Q15 multiply.
> Float would be too slow and non-deterministic on the M4/VSPA; fixed-point gives the
> PHY bit-exact, predictable timing."

**6. "Why do you keep SIMD out of `src/`?"**
> "Portability. `src/` is the algorithm. `lib/x86/` and `lib/platform/arm_ran/` are
> two implementations of the same `cn_*` API — AVX2 and NEON. CMake links the right
> one based on the target. If we ever ship on a third architecture, `src/` doesn't
> change."

**7. "How would you debug a SIMD bug?"**
> "Same way you debug any DSP bug — start with the scalar reference. The codebase
> always keeps a scalar fallback (e.g. the `_demod_bpsk` function called for the tail
> at [lib/x86/cn_demodulator.c:156](/home/cb24/workspace/nr_ue_phy/lib/x86/cn_demodulator.c#L156)).
> Run both paths on the same input, diff the output, and the lane that differs tells
> you where the SIMD pipeline goes wrong. If a permute is the suspect, dump the
> `__m256i` lane-by-lane with a debug helper before and after each step."

---

# Suggested order of attack

1. **I0 + I3** — internalise *why* SIMD and how to read intrinsic names. 30 min.
2. **I1 + I2** — get one AVX2 and one NEON minimal example compiling on a machine you
   own (RPi for NEON, any laptop for AVX2). 1 h.
3. **I4** — saturate vs wrap. Important for *every* SIMD interview question. 30 min.
4. **I6** — the BPSK demodulator walkthrough. Re-read the actual file in tree. 1 h.
5. **I7** — the descrambler walkthrough — this teaches branch-free SIMD. 1 h.
6. **I8** — the NEON QPSK demodulator. Pay particular attention to `vqrdmulhq_s16`. 1 h.
7. **I9** — read the interview talking points out loud. 30 min.

Total: about a working day if you stay focused. After this you'll have *literacy* — you
can read SIMD code, explain what it's doing, and answer interview questions confidently.
Fluency (writing it from scratch) is months of practice, but you don't need that.
