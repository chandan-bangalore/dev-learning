# 5G NR DL/UL Channel Chains — Reference

Source: `/home/cb24/workspace/refc/` (gNB-side reference PHY for DL TX,
UE-side reference PHY for UL TX).
3GPP Release 15 (TS 38.211 / 38.212 / 38.213 / 38.214).

This document has four parts:

1. **TX chains** — one line per channel, payload-in to antenna-out, in
   the order the refc code actually calls them. DL = gNB TX, UL = UE TX.
2. **RX chains** — antenna-in to payload-out. DL = UE RX, UL = gNB RX.
3. **Components** — what each block does, the 3GPP section, and the
   Rel-15 configuration space.
4. **Cross-channel summary tables** — fast lookup for both TX and RX.

Shared blocks (LDPC, polar, CRC, scrambler, modulator, IFFT+CP, channel
estimator, MIMO equalizer, soft demod, …) are named in the chains but
**described once** in Part 3.

---

## Part 1 — TX chains

### Top-level orchestration

**DL gNB TX** — [code/Dl/Gnb/Dl_Gnb_Transmitter.c:565](code/Dl/Gnb/Dl_Gnb_Transmitter.c#L565) runs five independent sub-chains (SSB / PDCCH / PDSCH / CSI-RS) into a shared frequency-domain grid `slotFreqOutput`, then [Dl_Gnb_Baseband.c:155](code/Dl/Gnb/Dl_Gnb_Baseband.c#L155) does the IFFT + CP per antenna.

**UL UE TX** — [code/Ul/Ue/Ul_Ue_Transmitter.c:169](code/Ul/Ue/Ul_Ue_Transmitter.c#L169) runs PUSCH / PUCCH / SRS into `slotFreqOutput`, PRACH has its own output stream (different sample rate / FFT size), and [code/Ul/Ue/Ul_Ue_Baseband.c:134](code/Ul/Ue/Ul_Ue_Baseband.c#L134) does the IFFT + CP per antenna.

---

### DL chains

#### PBCH (carries MIB inside SSB)

```
MIB (24 bits)
  → PBCH payload encoder (interleave + SFN/HRF/Kssb → 32 bits)
  → PBCH 1st scrambler (cell-ID seed)
  → CRC24C attach (→ 56 bits)
  → Polar encoder (K=56, N=512)
  → Polar rate matcher (→ E=864 bits)
  → 2nd scrambler (Gold PRS, cell-ID seed)
  → QPSK modulator (→ 432 symbols)
  → PBCH-DMRS generation (Gold PRS, cell-ID + SSB index)
  → SSB mapper (data + DMRS + PSS + SSS → 4-sym × 240-SC block)
  → Digital precoder (single layer)
  → [shared] IFFT + CP
```

Driver: [Dl_Gnb_Ssb_processData()](code/Dl/Gnb/Dl_Gnb_Ssb.c#L235).
Bit processing: [Dl_Gnb_PbchBitProcess.c:193 (CRC24C)](code/Dl/Gnb/Dl_Gnb_PbchBitProcess.c#L193), [:249 (Polar enc)](code/Dl/Gnb/Dl_Gnb_PbchBitProcess.c#L249), [:254 (Polar RM)](code/Dl/Gnb/Dl_Gnb_PbchBitProcess.c#L254).

#### PDCCH (carries DCI)

```
DCI payload (variable bits)
  → CRC24C attach (24 bits) with RNTI scrambling (last 16 bits XOR RNTI)
  → Polar encoder (K = payload+24, N=512)
  → Polar rate matcher (→ E = 108 · L bits, L = aggregation level 1/2/4/8/16)
  → Scrambler  (cinit = (nRnti<<16) + nIdPdcchDmrs)
  → QPSK modulator
  → PDCCH-DMRS generation (Gold PRS, cell-ID + nIdPdcchDmrs)
  → PDCCH mapper (CCEs → REGs, RE-group bundling, interleaver)
  → Digital precoder (1 layer)
  → [shared] IFFT + CP
```

Driver: [Dl_Gnb_Pdcch_processData()](code/Dl/Gnb/Dl_Gnb_Pdcch.c#L126).
Bit processing: [Dl_Gnb_PdcchBitProcess.c:92](code/Dl/Gnb/Dl_Gnb_PdcchBitProcess.c#L92).

#### PDSCH (carries DL-SCH transport blocks)

```
Transport block (TB, up to ~1.2 Mb)
  → CRC24A attach (TB-level) or CRC16 attach
  → Code-block segmentation
        (Kcb_max = 8448 for BG1, 3840 for BG2; each CB gets CRC24B if multiple CBs)
  → LDPC encoder, BG1 or BG2 (BG1 for high rate / large TB)
  → LDPC rate matcher
        (circular-buffer puncture/repeat per RV ∈ {0,1,2,3}, bit interleaver)
  → CB concatenation
  → Scrambler  (cinit = (nRnti<<15) + (q<<14) + nIdDataScrambling)
  → Modulator (QPSK / 16-QAM / 64-QAM / 256-QAM, per codeword)
  → Layer mapper (1-4 layers / codeword; up to 8 layers via 2 codewords)
  → PDSCH-DMRS + PTRS generation (Gold PRS, cell-ID + nScid)
  → PDSCH mapper (RE allocation per RB / symbol / port)
  → Digital precoder (codebook or non-codebook, up to 8 ports)
  → [shared] IFFT + CP
```

Driver: [Dl_Gnb_Pdsch_processData()](code/Dl/Gnb/Dl_Gnb_Pdsch.c#L235).
Bit processing: [Dl_Gnb_PdschBitProcess.c:235](code/Dl/Gnb/Dl_Gnb_PdschBitProcess.c#L235).

#### SSB composite (PSS + SSS + PBCH)

The PBCH chain above produces only the PBCH symbols inside the SSB. The SSB itself is built by composing three signals on the same 4-symbol × 240-SC block:

```
SSB block:
  symbol 0: PSS (ZC, root determined by N_ID^(2) ∈ {0,1,2})
  symbol 1: PBCH-data + PBCH-DMRS
  symbol 2: SSS (m-sequence, derived from N_ID^(1), N_ID^(2))  +  PBCH-data + PBCH-DMRS
  symbol 3: PBCH-data + PBCH-DMRS
```

Inside `Dl_Gnb_Ssb.c`:

- **PSS** — `Dl_Cn_SyncSignalGeneration_processData()`: Zadoff-Chu length-127, three possible roots per `N_ID^(2)`.
- **SSS** — same function: m-sequence pair, length-127, derived from `N_ID^(1)` and `N_ID^(2)`.
- **PBCH-DMRS** — Gold PRS, seed `cinit = 2^11 · (i_SSB+1) · (⌊N_ID^cell/4⌋+1) + 2^6 · (i_SSB+1) + N_ID^cell mod 4`.
- **SSB mapper** — [Dl_Gnb_SsbMapper_processData()](code/Dl/Gnb/Dl_Gnb_Ssb.c#L355).

#### CSI-RS (channel-state reference signal)

```
(no payload — pure reference signal)
  → CSI-RS sequence generation (Gold PRS, cell-ID + nIdCsiRs, per slot/symbol)
  → CSI-RS mapper (sparse pattern per row config; FD-CDM2/4 across ports)
  → Per-antenna scaling (EPRE offset vs PDSCH)
  → [shared] IFFT + CP
```

Driver: `Dl_Cn_CsiRs_processData()`. No CRC, no encoder, no modulator (sequence is implicitly QPSK).

#### DMRS for PDSCH / PDCCH / PBCH

Always **Gold PRS** with channel-specific seeds. Generated inline as the last step before mapping in each chain above. The DMRS pattern (which REs are pilots) is also channel-specific and is described in the mapper for each chain.

---

### UL chains

#### PRACH (random access preamble)

```
preamble index (logical root, cyclic-shift index)
  → Zadoff-Chu generator (long format L=839 or short L=139)
  → Cyclic shift by Cv (per preamble index)
  → Zero-padding to IFFT length (1024 / 2048 / 4096 / 8192)
  → IFFT (PRACH-specific, separate from data IFFT)
  → Upsampling filter (long format only, to match cell sampling rate)
  → Phase rotator (per FD occasion)
  → CP insertion (format-specific length)
```

Driver: [Ul_Ue_Prach_processData()](code/Ul/Ue/Ul_Ue_Prach.c#L219).
ZC generator: [Ul_Ue_Prach.c:291](code/Ul/Ue/Ul_Ue_Prach.c#L291) (long) / [:313](code/Ul/Ue/Ul_Ue_Prach.c#L313) (short).
Finalize: [Ul_Ue_PrachFinalize.c:64](code/Ul/Ue/Ul_Ue_PrachFinalize.c#L64).

No CRC, no encoder, no modulator — preamble selection IS the information.

#### PUCCH Format 0 (1-2 UCI bits, 1-2 symbols, 1 PRB)

```
UCI bits (1-2)
  → cyclic-shift selection (1 bit → 2 shifts, 2 bits → 4 shifts)
  → Low-PAPR ZC sequence (length 12, per group/sequence-hopping)
  → RE mapping (1 PRB × {1,2} symbols)
  → [shared] IFFT + CP
```

The bits are encoded purely by choosing which cyclic shift of the base sequence to send. No coding, no modulation, no DMRS (the sequence itself is the reference).

Driver: [Ul_Ue_PucchFormat01_processData()](code/Ul/Ue/Ul_Ue_PucchFormat01.c).

#### PUCCH Format 1 (1-2 UCI bits, 4-14 symbols, 1 PRB)

```
UCI bits (1-2)
  → BPSK (1 bit) or QPSK (2 bits) modulation
  → cyclic shift of low-PAPR ZC base sequence
  → time-domain OCC spreading (length depends on # symbols)
  → RE mapping (1 PRB × {4..14} symbols, alternating data/DMRS in time)
  → [shared] IFFT + CP
```

DMRS is the same ZC base sequence on the non-data symbols (no separate DMRS generator).

Driver: [Ul_Ue_PucchFormat01_processData()](code/Ul/Ue/Ul_Ue_PucchFormat01.c).

#### PUCCH Format 2 (>2 UCI bits, 1-2 symbols, 1-16 PRBs)

```
UCI bits (3-1706)
  → block code (Reed-Muller for ≤11 bits) or Polar+RM (≥12 bits)
  → Scrambler (Gold PRS, cinit per nIdPucchScrambling + nRnti)
  → QPSK modulator
  → PUCCH-DMRS generation (Gold PRS, cinit per nIdPucchDmrs)
  → RE mapping (data on subcarriers {0,1,3,4,6,7,9,10}, DMRS on {2,5,8,11} per RB)
  → [shared] IFFT + CP
```

Driver: [Ul_Ue_PucchFormat2_processData()](code/Ul/Ue/Ul_Ue_PucchFormat2.c).

#### PUCCH Format 3 (>2 UCI bits, 4-14 symbols, 1-16 PRBs, **DFT-spread**)

```
UCI bits
  → block code (≤11 bits) or Polar+RM (≥12 bits)
  → Scrambler
  → π/2-BPSK or QPSK modulator
  → DFT spreader (per data symbol, length = M_PRB × 12)
  → cyclic shift of low-PAPR ZC sequence (for DMRS symbols only)
  → RE mapping (data + DMRS on separate OFDM symbols)
  → [shared] IFFT + CP
```

DMRS uses dedicated symbols (2 or 4 per slot) — same as PUSCH-DFT-s-OFDM style. No pre-DFT OCC.

Driver: [Ul_Ue_PucchFormat34_processData()](code/Ul/Ue/Ul_Ue_PucchFormat34.c).

#### PUCCH Format 4 (>2 UCI bits, 4-14 symbols, 1 PRB, **DFT-spread + pre-DFT OCC**)

```
UCI bits
  → block code or Polar+RM
  → Scrambler
  → π/2-BPSK or QPSK modulator
  → pre-DFT OCC spreading (length-2 or length-4 Walsh code → 2 or 4 UEs per RB)
  → DFT spreader (per data symbol)
  → cyclic shift of low-PAPR ZC (for DMRS symbols)
  → RE mapping (data + DMRS on separate OFDM symbols)
  → [shared] IFFT + CP
```

The pre-DFT OCC is what lets multiple UEs share the same 1-PRB resource — it's the multi-user feature for PUCCH F4.

Driver: [Ul_Ue_PucchFormat34_processData()](code/Ul/Ue/Ul_Ue_PucchFormat34.c).

#### PUSCH — CP-OFDM (`transformPrecoding = disabled`)

```
Transport block (TB)
  → CRC24A attach
  → Code-block segmentation (+CRC24B per CB if multiple CBs)
  → LDPC encoder (BG1 or BG2)
  → LDPC rate matcher (per RV)
  → CB concatenation
  → UCI multiplexing (if HARQ-ACK / CSI piggybacked, see Data-and-Control mux)
  → Scrambler (cinit = (nRnti<<15) + nIdDataScrambling)
  → Modulator (QPSK / 16-QAM / 64-QAM / 256-QAM)
  → Layer mapper (1-4 layers)
  → PUSCH-DMRS generation (Gold PRS, cell-ID + nIdPuschDmrs)
  → PUSCH mapper (RE allocation; DMRS on comb-2, data on non-DMRS REs of DMRS symbol)
  → Codebook / non-codebook digital precoder
  → [shared] IFFT + CP
```

#### PUSCH — DFT-s-OFDM (`transformPrecoding = enabled`)

```
Transport block (TB)
  → CRC24A
  → CB segmentation (+CRC24B)
  → LDPC enc → LDPC RM → CB concat
  → UCI mux
  → Scrambler
  → π/2-BPSK or QPSK / 16-QAM / 64-QAM modulator
  → DFT spreader (per OFDM symbol, length = M_PRB × 12)        ← extra step
  → Layer mapper (always 1 layer — DFT-s-OFDM is single-layer in Rel-15)
  → PUSCH-DMRS generation (low-PAPR ZC `r_u,v`, NOT Gold)      ← different gen
  → PUSCH mapper (forced numDmrsCdmGrpsNoData = 2 → no data in DMRS symbol)
  → Codebook precoder (typically identity for single layer)
  → [shared] IFFT + CP
```

Driver: [Ul_Ue_Pusch_processData()](code/Ul/Ue/Ul_Ue_Pusch.c#L380).
Data encoder: [Ul_Ue_PuschDataEncoder.c:99](code/Ul/Ue/Ul_Ue_PuschDataEncoder.c#L99).
DMRS+PTRS gen/map: [Ul_Cn_PuschDmrsPtsGenMapper](code/Ul/Cn/Ul_Cn_PuschDmrsPtsGenMapper.c).

#### SRS (sounding reference signal)

```
(no payload — pure reference signal)
  → Low-PAPR ZC sequence generation (`r_u,v(n)`)
  → Cyclic shift per port
  → Frequency hopping (group / sequence hopping)
  → Comb-mapping (comb-2 or comb-4 → sparse in frequency)
  → RE mapping (1-4 antenna ports)
  → [shared] IFFT + CP
```

Driver: [Ul_Ue_Sounding_processData()](code/Ul/Ue/Ul_Ue_Sounding.c#L107).

---

### Shared baseband (both DL and UL)

```
slotFreqOutput (frequency-domain grid, per antenna port)
  → Common phase correction (CFO compensation, frequency domain)
  → IFFT-shift (DC-to-Nyquist subcarrier remap)
  → IFFT (size 256 ... 8192, 1/√N scaling)
  → CP insertion (Normal CP: 160/144 samples @ 30.72 MHz; Extended CP: 512)
  → Time-domain samples per antenna (output to RF)
```

DL: [Dl_Gnb_Baseband.c:155](code/Dl/Gnb/Dl_Gnb_Baseband.c#L155).
UL: [Ul_Ue_Baseband.c:134](code/Ul/Ue/Ul_Ue_Baseband.c#L134).

---

## Part 2 — RX chains

### Top-level orchestration

**DL UE RX** — entry [code/Dl/Ue/Dl_Ue_Receiver.c:473](code/Dl/Ue/Dl_Ue_Receiver.c#L473). Slot-wide CP removal + FFT produce a frequency-domain grid, then per-channel sub-pipelines run (PBCH, PDCCH, PDSCH). PSS/SSS detection and CFO estimation live in the dl_sync controller (separate from the steady-state receiver).

**UL gNB RX** — entry [code/Ul/Gnb/Ul_Gnb_Receiver.c:596](code/Ul/Gnb/Ul_Gnb_Receiver.c#L596). CFO compensation then CP removal + FFT, then per-channel sub-pipelines (PUSCH, PUCCH, SRS). PRACH has its own front-end (different sample rate and FFT size).

---

### DL receive chains

## UE cold-start: what happens before PSS/SSS

The receiver chains in Part 2 assume the UE already knows the carrier frequency, the cell-ID, and the slot/frame timing. At power-on it knows none of that. PSS/SSS is **step 5-7 out of a 15-step procedure**. Steps 1-4 are what *enable* PSS to be tractable in the first place — without them, blind correlation across an entire band would burn the battery and never converge.

### The 15-step boot procedure

```
   power-on
      │
   ┌──┴──────────────────────────────────────────────-┐
   │ 1.  Band selection (priority list / stored info) │  ← select the 5g freq band from list {n1, n3, n28, n78, …}. Scanning all frequencies randomly would be too slow.
   │ 2.  Frequency raster scan (step through GSCN)    │  ← checks predefined valid synchronization frequencies (3500.000MHz, 3500.144MHz, 3500.288MHz, etc)
   │ 3.  Coarse AGC settle                            │  ← measure UE rxd signal strength, if rxd signal is too strong or weak, UE inc/dec RF gain to make the signal usable. Fine tuning happens after sync. 
   │ 4.  Wait for one SSB burst window (~20 ms)       │  ← default periodicity
   ├──────────────────────────────────────────────────┤
   │ 5.  PSS correlation (3 root hypotheses)          │  ← time + N_ID^(2)
   │ 6.  Coarse CFO estimate + correct                │
   │ 7.  SSS detection (m-sequence)                   │  ← N_ID^(1), cell-ID
   │ 8.  PBCH-DMRS detect → SSB index                 │  ← SFN ambiguity break
   │ 9.  Fine CFO + timing tracking                   │
   │ 10. PBCH polar decode → MIB                      │  ← SFN, k_SSB, SCS
   ├──────────────────────────────────────────────────┤
   │ 11. SIB1 acquisition (PDCCH SI-RNTI → PDSCH)     │  ← RACH cfg, BWP cfg
   │ 12. PLMN selection / cell-bar check              │
   │ 13. Random access (PRACH → RAR → Msg3 → Msg4)    │  ← C-RNTI obtained
   │ 14. RRC connection setup                         │
   │ 15. Steady state — DCI on C-RNTI drives PDSCH/PUSCH
   └──────────────────────────────────────────────────┘
```

### Stage 1 — Finding *where to look*

Before PSS detection can run, the UE has to decide which RF frequency to point its LO at. Three concepts gate this:

- **Bands** — the UE has a stored list of bands it supports (n1, n3, n28, n78, …) and a priority order (last-used first, then stored info, then full scan).
- **Frequency raster** — 5G's **synchronization raster** defines a discrete set of frequencies (GSCN values) where an SSB *can* exist. SSBs cannot sit at arbitrary frequencies. The raster spacing depends on the band: ~1.44 MHz for sub-3 GHz (FR1 low), ~17.28 MHz for sub-24.25 GHz (FR1 mid), 17.28 MHz for FR2.
- **SSB burst period** — by default 20 ms. The gNB transmits an SSB burst every 20 ms; the UE must dwell at each candidate frequency long enough to catch one.

Per GSCN candidate, the rough cost is: tune LO, settle AGC, wait ≥ 20 ms for the SSB window, run PSS correlator. Multiply by the number of GSCN points in the band — that's the cell-search budget.

### Stage 2 — Locking onto the cell (steps 5-10)

Once the LO is on a GSCN point that actually has an SSB:

1. **PSS correlation** — slide a time-domain correlator against the 3 Zadoff-Chu PSS root sequences. A peak above threshold gives **coarse symbol timing** and the cell's `N_ID^(2) ∈ {0, 1, 2}`.
2. **Coarse CFO estimate and correction** — TCXOs in cheap UEs drift by 2-20 ppm. At 3.5 GHz that's 7-70 kHz, big compared to 15 kHz SCS. The PSS peak's phase ramp gives the residual LO offset; correct it before SSS.
3. **SSS detection** — m-sequence at the symbol position offset from PSS; gives `N_ID^(1) ∈ {0..335}` and the half-frame indicator. Physical cell-ID = `3·N_ID^(1) + N_ID^(2)` ∈ {0..1007}.
4. **PBCH-DMRS detection** — 4 (FR1 low-band) or 8 (FR1 above 3 GHz / FR2) candidate SSB indices. Correlation against each DMRS hypothesis tells you which SSB in the burst this is — fixes the SFN-mod-4 or SFN-mod-8 ambiguity.
5. **Fine CFO + timing tracking** — using PBCH-DMRS pilots.
6. **PBCH polar decoding** — CA-SCL list size 4, CRC24C check. Yields the MIB: SFN (10 bits), half-frame, k_SSB (offset from SSB to the carrier center), subCarrierSpacingCommon, dmrs-TypeA-Position.

After stage 2 the UE knows: **carrier frequency, cell-ID, SFN, frame timing, subcarrier spacing**. Now real receiver activity becomes possible.

### Stage 3 — Joining the cell (steps 11-15)

- **SIB1 acquisition** — decode the Type 0 common search space PDCCH (RNTI = SI-RNTI) → find SIB1 PDSCH grant → decode SIB1. SIB1 has the RACH config, full BWP config, PLMN list, scheduling info for other SIBs.
- **PLMN selection + cell-bar check** — does this cell belong to a network we're allowed on? If not, restart with the next GSCN.
- **Random access** — pick a PRACH preamble, transmit on the configured PRACH occasion, wait for RAR (PDCCH with RA-RNTI → PDSCH), send Msg3, receive Msg4 contention resolution. End of RACH: UE holds a **C-RNTI**.
- **RRC setup** — higher-layer handshake to establish the RRC connection.
- **Steady state** — UE monitors PDCCH for DCI scrambled with its C-RNTI. Each DCI triggers one of the receive chains in Part 2 of this document.

### What the UE knows at each stage (cumulative)

| After step | UE knows | Code in refc |
|---|---|---|
| 5 (PSS) | coarse timing, `N_ID^(2)` | [dl_sync/src/dl_sync_pss_detection.c](Dl/Ue/dl_sync/src/dl_sync_pss_detection.c) |
| 7 (SSS) | full cell-ID (1008 values), half-frame | [dl_sync/src/dl_sync_sss_detection.c](Dl/Ue/dl_sync/src/dl_sync_sss_detection.c) |
| 8 (PBCH-DMRS) | SSB index, SFN-mod-{4,8} | [code/Dl/Ue/Dl_Ue_PbchChest.c](code/Dl/Ue/Dl_Ue_PbchChest.c) |
| 10 (MIB) | SFN, k_SSB, SCS common, frame timing | [code/Dl/Ue/Dl_Ue_Pbch.c](code/Dl/Ue/Dl_Ue_Pbch.c) |
| 11 (SIB1) | RACH config, BWP config, PLMN list | (MAC/RRC, above PHY) |
| 13 (RACH) | C-RNTI, UL timing advance | PRACH TX + PDCCH/PDSCH RX on RA-RNTI |
| 14 (RRC) | full UE-specific cfg | (RRC, above PHY) |
| 15 (steady) | per-slot DCI grants | normal PDCCH/PDSCH/PUSCH chains |

### Why this matters for the PHY

Most of the steady-state PHY code (the chains in Parts 1-2) is the easy part — the hard parts are:

- **Step 4** — knowing when an SSB will arrive without yet knowing the frame timing. Solved by the periodic 20 ms SSB burst contract: you just wait one period and you're guaranteed to see something if a cell exists at that frequency.
- **Steps 5-6** — recovering timing and frequency from a signal you can barely see, in noise, with multipath. PSS correlation gain comes from the length of the sequence (127 samples).
- **Step 13** — first transmission on PRACH, before timing advance is known. The PRACH preamble has a long CP and guard time precisely to tolerate the unknown round-trip delay.

Once you're at step 15, the PHY runs the chains documented in Parts 1-2 of this document. Everything before that is what makes those chains possible.

```
```

#### SSB cell search + PBCH RX

```
RF time-domain samples
  → PSS xcorr (3 candidate roots → N_ID^(2), coarse timing)
  → SSS m-sequence detection (→ N_ID^(1), half-frame, cell-ID complete)
  → CFO estimation (PBCH-DMRS xcorr, fine)
  → CP removal + FFT
  → PBCH-DMRS generation (Gold PRS, 8 SSB candidate seeds)
  → PBCH-DMRS correlation (pick best SSB index + half-frame)
  → PBCH-DMRS compensation (phase/amp correct)
  → Channel estimation (Makima freq interp + Wiener time filter)
  → PBCH RE extraction (data REs only, exclude DMRS)
  → 1×1 MIMO equalizer (LMMSE)
  → QPSK soft demodulation (LLRs)
  → 2nd descrambling (Gold PRS)
  → Polar rate de-matcher
  → CA-SCL polar decoder (K=32, E=864, list size 4)
  → CRC24C check
  → 1st descrambling (cell-ID seed)
  → MIB de-interleave (split SFN/HRF/Kssb from MIB body)
  → MIB (24 bits) out
```

PSS: [dl_sync/src/dl_sync_pss_detection.c](Dl/Ue/dl_sync/src/dl_sync_pss_detection.c).
SSS: [dl_sync/src/dl_sync_sss_detection.c](Dl/Ue/dl_sync/src/dl_sync_sss_detection.c).
CFO: [Dl_Ue_B2M_ReferenceTerminal_CFO_estimator.c:134](code/Dl/Ue/Dl_Ue_B2M_ReferenceTerminal_CFO_estimator.c#L134).
PBCH chest: [Dl_Ue_PbchChest.c:143-284](code/Dl/Ue/Dl_Ue_PbchChest.c#L143).
PBCH RX: [Dl_Ue_Pbch.c:102-304](code/Dl/Ue/Dl_Ue_Pbch.c#L102).

#### PDCCH RX (blind DCI search)

```
frequency-domain symbols (per slot, shared FFT output)
  → CCE-to-REG mapping (CORESET-specific interleaver)
  → PDCCH-DMRS generation (Gold PRS, cell-ID or scrambling-ID seed)
  → PDCCH-DMRS channel estimation (per CORESET symbol)
  → PDCCH RE demapping (extract data REs, layer + chan estimates)
  → 1×1 MIMO equalizer (LMMSE)
  → QPSK soft demodulation
  → Descrambler (Gold PRS, cinit = (nRnti<<16) + nId)         ← RNTI-keyed
  → Polar rate de-matcher
  → CA-SCL polar decoder
  → CRC24C ⊕ RNTI check                                       ← filter step
  →   if CRC pass → DCI bits out
  →   else → discard (try next candidate / next RNTI per dci-format, AL, cand_idx)
```

Driver: [Dl_Ue_Pdcch.c:121](code/Dl/Ue/Dl_Ue_Pdcch.c#L121).
Decoder: [Dl_Ue_PdcchDecoder.c:96](code/Dl/Ue/Dl_Ue_PdcchDecoder.c#L96).

The blind search is an **outer loop** over (aggregation level, candidate index, RNTI type). For each combination the chain above runs and the CRC check filters out the failed candidates. Only the survivors are passed to the DCI format decoder ([Dl_Ue_DciDecoder.c](code/Dl/Ue/Dl_Ue_DciDecoder.c)).

#### PDSCH RX (DL-SCH data)

```
frequency-domain symbols (per slot)
  → PDSCH-DMRS generation (Gold PRS, cell-ID + nScid seed)
  → DMRS-based channel estimation
        (Makima freq interp + Wiener time interp, per RX antenna × TX layer)
  → PDSCH RE allocation calc (exclude DMRS, PTRS, CSI-RS REs from RM)
  → Per-symbol PDSCH demapper (extract data REs + per-RE chan estimate)
  → Per-symbol MIMO equalizer (LMMSE, supports 1×1, 1×N, 2×N, 4×N)
  → Layer demapper (combine 1-4 layers → codeword)
  → Soft demodulation (QPSK / 16-QAM / 64-QAM / 256-QAM, scaled by NPS)
  → Descrambler (Gold PRS, cinit = (nRnti<<15) + nIdDataScrambling)
  → LDPC rate de-matcher
        (bit-deinterleaver, circular-buffer fill, HARQ combine on retx)
  → LDPC decoder (BG1 or BG2, layered min-sum or sum-product)
  → Per-CB CRC24B check
  → CB concatenation
  → TB CRC24A check
  →   pass → TB out, ACK
  →   fail → NACK + HARQ buffer retained for combining
```

Driver: [Dl_Ue_Pdsch.c:143](code/Dl/Ue/Dl_Ue_Pdsch.c#L143).
Chest: [Dl_Ue_Pdsch.c:245](code/Dl/Ue/Dl_Ue_Pdsch.c#L245).
Per-symbol eq: [Dl_Ue_Pdsch.c:311-339](code/Dl/Ue/Dl_Ue_Pdsch.c#L311).
Decoder: [Dl_Ue_Pdsch.c:520](code/Dl/Ue/Dl_Ue_Pdsch.c#L520).

#### CSI-RS measurement

In refc, **payload-carrying CSI-RS measurement is not fully implemented in the steady-state receiver** — only its RE positions are computed so PDSCH rate-matching excludes them ([Dl_Ue_PdschParameter.h](code/Dl/Ue/Dl_Ue_PdschParameter.h)). The cell-search side computes SS-RSRP / SS-RSRQ / SS-SNR from PSS / SSS / PBCH-DMRS in [dl_sync/src/dl_sync_ss_measurement.c](Dl/Ue/dl_sync/src/dl_sync_ss_measurement.c) (no CSI-RS).

A full CSI-RS measurement chain (when implemented) would look like:

```
frequency-domain symbols
  → CSI-RS RE extraction (sparse pattern per row config)
  → CSI-RS sequence generation (Gold PRS, cell-ID + nIdCsiRs)
  → LS pilot channel estimate per port
  → RSRP   = mean |y · conj(ref)|²
  → RSRQ   = (N · RSRP) / RSSI
  → SINR   = signal_power / noise_power
  → CQI / RI / PMI selection (codebook search)
```

---

### UL receive chains

#### PRACH RX (preamble detection)

```
RF time-domain samples (PRACH-specific sample rate)
  → CFO compensation
  → PRACH baseband (CP removal, FFT, NB-IoT-like resampling)
  → for each ZC root in cell's root-sequence list:
       → multiply received × conj(root ZC)
       → zero-pad to IFFT length
       → IFFT (FFT-based circular correlation)
       → magnitude squared
       → accumulate across antennas
       → search peaks across cyclic shifts × TA hypotheses
  → if peak > threshold:
       → output { preambleIndex, timingAdvance }
```

Driver: [Ul_Gnb_Prach.c:233-382](code/Ul/Gnb/Ul_Gnb_Prach.c#L233).
Indication: [Ul_Gnb_Receiver.c:102](code/Ul/Gnb/Ul_Gnb_Receiver.c#L102).

Long format (L_RA=839) and short format (L_RA=139) share the same correlation structure; only the FFT size and accumulation length differ.

#### PUCCH F0 RX (cyclic-shift detection)

```
frequency-domain RE (1 PRB × 1-2 symbols, already FFT'd)
  → Base ZC sequence generation (per group/sequence hopping)
  → for each TA hypothesis:
       → phase-rotate received
       → IDFT (length-12)
       → correlate with each of 4 (or 12) cyclic-shift hypotheses
       → record correlation magnitude
  → peak detection → { harqAck, sr, timingAdvance }
```

Driver: [Ul_Gnb_PucchFormat01.c:156-328](code/Ul/Gnb/Ul_Gnb_PucchFormat01.c#L156).

No DMRS, no MMSE — F0 is purely sequence selection. The detected cyclic shift IS the UCI value.

#### PUCCH F1 RX

```
frequency-domain RE (1 PRB × {4..14} symbols)
  → Base ZC sequence generation
  → IDFT per symbol
  → DMRS-based channel estimation (alternate symbols are DMRS)
  → Time-domain OCC despreading (length depends on # symbols)
  → Cyclic-shift hypothesis test against the 12 cyclic-shifted variants
  → peak detection → { harqAck, sr, timingAdvance }
```

Driver: [Ul_Gnb_PucchFormat01.c:349-407](code/Ul/Gnb/Ul_Gnb_PucchFormat01.c#L349).

#### PUCCH F2 RX

```
frequency-domain RE
  → DMRS-based channel estimation (DMRS on SCs {2,5,8,11}/RB)
  → Data + DMRS demapping
  → 1×N MIMO equalizer (LMMSE)
  → QPSK soft demodulation
  → Descrambler (Gold PRS, cinit per nIdPucchDataScrambling + nRnti)
  → UCI decoder (block code for ≤11 bits, polar for ≥12)
  → UCI bits out (HARQ + SR + CSI-Part1 + CSI-Part2)
```

Driver: [Ul_Gnb_PucchFormat2.c:100-254](code/Ul/Gnb/Ul_Gnb_PucchFormat2.c#L100).

#### PUCCH F3 RX (DFT-spread, no pre-DFT OCC)

```
frequency-domain RE (1-16 PRBs × {4..14} symbols)
  → DMRS-based channel estimation (DMRS on dedicated symbols)
  → Data + DMRS demapping
  → 1×N MIMO equalizer (LMMSE)
  → IDFT (per OFDM symbol; reverses TX DFT spread)               ← TP undo
  → Soft demodulation (π/2-BPSK or QPSK)
  → Descrambler (Gold PRS)
  → UCI decoder (block code or polar)
```

Driver: [Ul_Gnb_PucchFormat34.c:183-646](code/Ul/Gnb/Ul_Gnb_PucchFormat34.c#L183).

#### PUCCH F4 RX (DFT-spread + pre-DFT OCC)

```
frequency-domain RE (1 PRB × {4..14} symbols)
  → DMRS chest + demap + MMSE  (same as F3)
  → IDFT                                                         ← TP undo
  → pre-DFT OCC despreading (length-2 or length-4 Walsh)         ← MU-PUCCH undo
  → Soft demodulation
  → Descrambler
  → UCI decoder
```

Driver: same file as F3 ([Ul_Gnb_PucchFormat34.c:574-637](code/Ul/Gnb/Ul_Gnb_PucchFormat34.c#L574)).

#### PUSCH RX (CP-OFDM and DFT-s-OFDM share most of the chain)

```
frequency-domain RE (per slot, shared FFT)
  → PUSCH-DMRS generation (Gold for CP-OFDM, low-PAPR ZC for DFT-s-OFDM)
  → DMRS-based channel estimation
        (freq interp + optional time avg, per RX antenna × TX layer)
  → Per-symbol PUSCH demapper (exclude DMRS / PTRS REs)
  → Per-symbol MIMO equalizer (LMMSE, 1×N or 2×N)
  → IF (transformPrecoderFlag == 1):                             ← ONLY diff
        → Transform deprecoder (IDFT per OFDM symbol, length M_PRB·12)
  → Layer demapper (combine layers → codeword)
  → Data/control de-multiplex (extract UCI piggyback if any)
  → Soft demodulation (per-codeword Qm)
  → Descrambler (Gold PRS, cinit = (nRnti<<15) + nIdDataScrambling)
  → LDPC rate de-matcher (+ HARQ combine)
  → LDPC decoder (BG1 / BG2)
  → CB CRC24B check + TB CRC24A check
  → TB out + UCI out
```

Driver: [Ul_Gnb_Pusch.c:194](code/Ul/Gnb/Ul_Gnb_Pusch.c#L194).
Chest: [Ul_Gnb_Pusch.c:372](code/Ul/Gnb/Ul_Gnb_Pusch.c#L372).
TP branch: [Ul_Gnb_Pusch.c:529-565](code/Ul/Gnb/Ul_Gnb_Pusch.c#L529).
Decoder: [Ul_Gnb_Pusch.c:934](code/Ul/Gnb/Ul_Gnb_Pusch.c#L934).

#### SRS RX (channel sounding)

```
frequency-domain RE (sparse comb pattern)
  → SRS reference sequence generation (low-PAPR ZC + cyclic shift)
  → SRS channel estimation (LS on sounding REs, per RX × TX-port)
  → Per-RB SNR computation
  → Wideband CQI / RI / PMI estimate (SVD on H·H†)
  → Timing-advance estimate (impulse response peak)
  → Output: H matrix + TA + SNR (no payload)
```

Driver: [Ul_Gnb_Srs.c:134-392](code/Ul/Gnb/Ul_Gnb_Srs.c#L134).

---

### Shared RX baseband

```
RF time-domain samples (per antenna)
  → CFO compensation (frequency-domain phase rotation OR time-domain)
  → CP removal (skip the first 144/160 samples per symbol)
  → FFT (size 256 ... 8192, 1/√N scaling)
  → frequency-domain grid output (per RX antenna)
```

DL: [Dl_Ue_Baseband.c:177](code/Dl/Ue/Dl_Ue_Baseband.c#L177).
UL: [Ul_Gnb_Baseband.c:132](code/Ul/Gnb/Ul_Gnb_Baseband.c#L132).

---

## Part 3 — Components

### 3.1 Bit-level processing (TX)

#### CRC attach

| Type       | Polynomial deg | Where used |
|---|---|---|
| **CRC24A** | 24 | PDSCH-TB, PUSCH-TB |
| **CRC24B** | 24 | PDSCH/PUSCH per-CB (when segmentation) |
| **CRC24C** | 24 | PBCH, PDCCH (RNTI-scrambled) |
| **CRC16**  | 16 | UCI ≥ 20 bits on PUCCH F2/F3/F4 + PUSCH (TS 38.212 §6.3.1.2) |
| **CRC11**  | 11 | UCI 20-1706 bits (used in some segmentation paths) |
| **CRC6**   | 6  | UCI 12-19 bits (TS 38.212 §6.3.1.2) |

Polynomials: TS 38.212 §5.1. Rel-15 supports all six.
On PDCCH, CRC24C is XOR-masked with the **RNTI** in its last 16 bits, so a UE only "sees" its own DCI when the post-decoding CRC checks out — this is how the UE filters its messages from the shared search space.

#### Code-block segmentation

When `K_TB + 24 > K_cb_max`, the TB is split into multiple CBs of size ≤ K_cb_max, and each CB gets its own CRC24B. Otherwise no per-CB CRC.

- BG1: `K_cb_max = 8448` bits, info `Kb = 22 · Zc` where Zc ∈ Rel-15 lifting sizes.
- BG2: `K_cb_max = 3840` bits, `Kb = 10 · Zc` (or 9/8/6 depending on `Kb` selection rule).

TS 38.212 §5.2.2.

#### LDPC encoder

Quasi-cyclic LDPC, two base graphs ([Cn_LdpcEncoder.c](code/Cn/Cn_LdpcEncoder.c)):

- **BG1** — for high code rate (R ≥ 1/3) or large TB (> 292 bits). Mother rate 1/3. 22 systematic × 46 parity columns of size Zc.
- **BG2** — for low code rate (R < 1/3) or small TB (≤ 292 bits). Mother rate 1/5.

Lifting sizes (Zc): set of 51 values in 8 sets (TS 38.212 Table 5.3.2-1). Selection: smallest Zc such that `Kb · Zc ≥ K_TB + 24`.

#### LDPC rate matcher

Three stages (TS 38.212 §5.4.2):

1. **Bit selection** from the circular buffer starting at `k_0(rv)`, with skipping of filler bits.
2. **Bit interleaver** (row-column).
3. **Repetition or puncturing or shortening** to hit the target `E` (REs available · Qm).

RV ∈ {0,1,2,3} for HARQ. RV=0 starts at the systematic bits; RV=2 starts mid-buffer; etc.

#### Polar encoder

[Cn_PolarEncoder.c](code/Cn/Cn_PolarEncoder.c). Used for **DCI (PDCCH)**, **MIB (PBCH)**, **UCI of ≥12 bits**.
TS 38.212 §5.3.1.

- `N` chosen from {32, 64, 128, 256, 512, 1024}.
- **PBCH**: K=56 (32 payload + 24 CRC), N=512 fixed.
- **PDCCH**: K = DCI_bits + 24, N=512 (with 18-bit CRC scrambled by RNTI inside the 24).
- **UCI**: K ≥ 12, N up to 1024.

Frozen bits chosen per TS 38.212 Table 5.3.1.2-1 (reliability sequence Q_N^max).

#### Polar rate matcher

TS 38.212 §5.4.1. Subblock interleaver + bit selection (puncture / shorten / repeat) to hit `E`.

#### Reed-Muller / block code (small UCI)

For UCI ≤ 11 bits on PUCCH F2/F3/F4 — TS 38.212 §5.3.3. The code is a hand-tuned shortened RM-like generator matrix (Table 5.3.3.2-1 for 3-11 bits).

#### Scrambler

XOR with a **Gold pseudo-random sequence** built from two 31-bit M-LFSRs (TS 38.211 §5.2.1). The seed `c_init` depends on the channel:

| Channel | c_init seed |
|---|---|
| PDSCH | `(nRnti << 15) + (q << 14) + nIdDataScrambling`  (q = codeword index) |
| PUSCH | `(nRnti << 15) + nIdDataScrambling` |
| PDCCH | `(nRnti << 16) + nIdPdcchDmrsScrambling` |
| PUCCH F2/3/4 | `(nRnti << 15) + nIdPucchDataScrambling` |
| PBCH 1st | depends on cell-ID and `mod(SFN, 8)` |
| PBCH 2nd | depends on cell-ID, scrambled per TS 38.212 §7.1.2 |

The scrambler decorrelates inter-cell + inter-UE transmissions on shared resources (multi-RNTI separation; also why a UE only decodes "its own" data after correct descrambling).

Implementation: [Cn_Prs.c](code/Cn/Cn_Prs.c) for the Gold sequence + [Dl_Gnb_Scrambler.c](code/Dl/Gnb/Dl_Gnb_Scrambler.c) / [Ul_Ue_PuschScrambler.c](code/Ul/Ue/Ul_Ue_PuschScrambler.c) for the XOR.

#### Modulator

Gray-coded constellation (TS 38.211 §5.1):

| Name | Qm (bits/sym) | Rel-15 channels |
|---|---|---|
| **π/2-BPSK** 	| 1 | DFT-s-OFDM PUSCH, PUCCH F3/F4 |
| **BPSK** 		| 1 | PUCCH F1 (1-bit UCI) |
| **QPSK** 		| 2 | PBCH, PDCCH, PDSCH, PUSCH, PUCCH F1/2/3/4 |
| **16-QAM** 	| 4 | PDSCH, PUSCH, PUCCH F3 (less common) |
| **64-QAM** 	| 6 | PDSCH, PUSCH |
| **256-QAM** 	| 8 | PDSCH, PUSCH (capability-gated) |

Implementation: [Cn_Modulator.c](code/Cn/Cn_Modulator.c), with a specialized [Dl_Gnb_ModulatorScaled.c](code/Dl/Gnb/Dl_Gnb_ModulatorScaled.c) for QPSK with Q13 power scaling (used by PBCH/PDCCH/SSB).

#### Layer mapper

PDSCH / PUSCH only. Distributes modulated symbols across spatial layers per TS 38.211 §7.3.1.3 / §6.3.1.3.

- **PDSCH Rel-15**: 1-4 layers per codeword. 5-8 layers requires 2 codewords (layer 1-4 from CW0, 5-8 from CW1).
- **PUSCH Rel-15**: 1-4 layers, single codeword. DFT-s-OFDM is always single-layer.

Implementation: [Dl_Gnb_LayerMapper.c](code/Dl/Gnb/Dl_Gnb_LayerMapper.c), [Ul_Ue_LayerMapper.c](code/Ul/Ue/Ul_Ue_LayerMapper.c).

#### Transform precoder (DFT spreader)

PUSCH + PUCCH F3/F4 only (UL). Applies a length-`M_PRB · 12` DFT to each OFDM symbol's modulation symbols **before** SC mapping. Turns CP-OFDM into DFT-s-OFDM (a.k.a. SC-FDMA) so the time-domain waveform retains low PAPR.

In Rel-15 PUSCH this is gated by the `transformPrecoding` IE; mandatory when π/2-BPSK is configured.

Implementation: [Ul_Ue_TransformPrecoder.c:71](code/Ul/Ue/Ul_Ue_TransformPrecoder.c#L71).

#### Digital precoder

Maps layers to antenna ports. Two modes:

- **Codebook-based**: precoding matrix index (TPMI) selected by the gNB and signalled in DCI. The precoding matrix is read from TS 38.211 Tables 6.3.1.5-x (1-4 layers, 2-port and 4-port codebooks).
- **Non-codebook**: precoding implicit from sounding (SRS-based reciprocity).

Implementation: [Dl_Gnb_DigitalPrecoder.c](code/Dl/Gnb/Dl_Gnb_DigitalPrecoder.c), [Ul_Ue_PuschPrecoder.c](code/Ul/Ue/Ul_Ue_PuschPrecoder.c).

---

### 3.2 Reference-signal generators

#### Gold pseudo-random sequence (PRS)

Two length-31 M-LFSRs XORed (TS 38.211 §5.2.1). One LFSR has fixed seed, the other gets `c_init` (channel-specific). Used **everywhere** a sequence needs to look random: scramblers, PDSCH/PDCCH/PBCH/PUCCH-F2+ DMRS, CSI-RS, SRS-scrambling.

Implementation: [Cn_Prs.c](code/Cn/Cn_Prs.c).

#### Low-PAPR Zadoff-Chu base sequences (`r_u,v(n)`)

TS 38.211 §5.2.2. Used where the **time-domain** signal must have low PAPR:

- DFT-s-OFDM PUSCH DMRS
- PUCCH F0/F1 (cyclic-shift selected sequences)
- PUCCH F3/F4 DMRS
- SRS
- PRACH long format (L_RA=839) and short format (L_RA=139)

Two flavours: computer-generated sequences (for short lengths < 36) and proper Zadoff-Chu (length ≥ 36). Parametrized by sequence group `u` (0..29), sequence index `v` (0 or 1), and cyclic shift α.

Implementation: [Ul_Cn_ReferenceSignalSeq.c](code/Ul/Cn/Ul_Cn_ReferenceSignalSeq.c).

#### m-sequence

Standalone maximum-length sequence (single LFSR). Used for **SSS**: a pair of length-127 m-sequences combined via cyclic shifts encoded with `N_ID^(1)` and `N_ID^(2)` so the UE can recover the full cell-ID after detecting both PSS and SSS.

#### Cyclic shift

Applies α = 2π·m/N to a base sequence. Three places it shows up:

- **PRACH**: `Cv = ...` chooses which preamble out of the 64 available in a cell (one root sequence → up to 64 cyclic-shifted variants).
- **PUCCH F0/F1**: cyclic shift selects the UCI value (F0) or separates UEs (F1).
- **PUSCH/PUCCH DMRS**: cyclic shift separates DMRS ports within a CDM group.

#### OCC (orthogonal cover code)

Walsh codes (lengths 2, 4 typical). Used to multiplex multiple UEs / layers / ports on the same RE set:

- **PUCCH F1**: time-domain OCC across the data symbols.
- **PUCCH F4**: pre-DFT OCC (lengths 2 or 4) to share one PRB across 2 or 4 UEs.
- **PDSCH/PUSCH DMRS**: OCC within a CDM group (lengths 2 in time, 2 in frequency).

---

### 3.3 DMRS Rel-15 configuration cap

DMRS Configuration Type → how DMRS REs are arranged in frequency
DMRS Mapping Type 		→ where DMRS is placed in time/symbols

| Channel 					| Config type 								| Max symbols (front-loaded + additional) | Max ports |
|---|---|---|---|
| **PDSCH** 				| Type 1 (comb-2) or Type 2 (comb-3-block) 	| 2 + 2 → 4 total 			| 8 (Type 1) / 12 (Type 2) |
| **PDCCH** 				| Type 1 only 								| 1 (mapped into CCEs) 		| 1 |
| **PBCH** 					| Custom (mapped into SSB) 					| within 4-symbol SSB block | 1 |
| **PUSCH (CP-OFDM)** 		| Type 1 or Type 2 							| 2 + 2 → 4 total 			| 8 (Type 1) / 12 (Type 2) |
| **PUSCH (DFT-s-OFDM)** 	| Type 1 only, single CDM group 			| 2 + 2 → 4 total 			| 1 (single layer mandatory) |
| **PUCCH F1/F3/F4**	 	| dedicated DMRS symbols					| up to 7 					| 1 |

Source: TS 38.211 §7.4.1.1 (PDSCH) / §6.4.1 (PUSCH).

---

### 3.4 Baseband (shared TX/RX)

#### IFFT (transmitter) / FFT (receiver)

Implementation: [Cn_Fft.c](code/Cn/Cn_Fft.c). Mixed-radix, sizes 32 ... 8192 supported. Output scaling `1/√N` keeps energy preserved.

#### Cyclic prefix insertion

TS 38.211 §5.3. Two configurations:

- **Normal CP** — symbol 0 of each ½-subframe has 160 samples of CP, others 144 (at 30.72 Msps reference rate; scales with SCS).
- **Extended CP** — fixed 512 samples per symbol, only allowed at SCS = 60 kHz.

Implementation: [Dl_Gnb_CpInsertion.c](code/Dl/Gnb/Dl_Gnb_CpInsertion.c), [Ul_Ue_CpInsertion.c](code/Ul/Ue/Ul_Ue_CpInsertion.c).

#### PRACH-specific baseband

PRACH has its own IFFT (length depends on PRACH format and cell sampling rate — typically larger than the data IFFT) and its own CP rules per format. The long formats (0/1/2/3) additionally need a polyphase upsampling filter to match the cell sampling rate (TS 38.211 §6.3.3).

---

### 3.5 RX-only components

These blocks have no TX counterpart and only run on the receive side.

#### CP removal

Strips the first `N_cp` samples of every OFDM symbol before FFT. The CP length table is the inverse of the insertion table ([Dl_Ue_CpRemoval.c](code/Dl/Ue/Dl_Ue_CpRemoval.c), [Ul_Gnb_CpRemoval.c](code/Ul/Gnb/Ul_Gnb_CpRemoval.c)). FFT then takes the remaining `N_FFT` samples per symbol.

#### CFO estimation and compensation

Two flavours in refc:

- **Time-domain xcorr** (PSS-based, [Dl_Ue_CfoEstimationXcor.c](code/Dl/Ue/Dl_Ue_CfoEstimationXcor.c) / [Ul_Gnb_CfoEstimationXcor.c](code/Ul/Gnb/Ul_Gnb_CfoEstimationXcor.c)) — coarse, used during cell search before FFT.
- **Frequency-bin estimate** (UL gNB, [Ul_Gnb_CfoEstimationFbin.c](code/Ul/Gnb/Ul_Gnb_CfoEstimationFbin.c)) — fine, post-FFT from DMRS phase ramp across symbols.

Compensation: [Ul_Gnb_CfoCompensator.c](code/Ul/Gnb/Ul_Gnb_CfoCompensator.c) — applies the inverse phase rotation either pre-FFT (time-domain ramp) or post-FFT (per-symbol constant).

#### Channel estimation (DMRS-based)

[Dl_Ue_ChannelEstimator.c](code/Dl/Ue/Dl_Ue_ChannelEstimator.c), [Ul_Gnb_ChannelEstimator.c](code/Ul/Gnb/Ul_Gnb_ChannelEstimator.c). Three stages:

1. **Pilot extraction** — pull DMRS REs out of the grid using the same comb-2 / comb-3 / dedicated-symbol patterns as TX mapped them in.
2. **Frequency interpolation** — Makima (modified Akima) interpolation across pilot SCs to recover channel at data SCs.
3. **Time interpolation / filtering** — Wiener filter or simple average across the multiple DMRS symbols (front-loaded + additional) in a slot.

Output: `H[nRx][nTxLayer][symbol][SC]`, ready for MIMO equalizer.

Used by PBCH, PDCCH, PDSCH, PUSCH, PUCCH F2/F3/F4, SRS.

Linear interpolation: 
h(k) = h_left + alpha x (h_right - h_left)
where,
alpha = (k - left_index) / (right_index - left_index)


#### MIMO equalizer

[Dl_Ue_MimoDetectorLmmseEqualizer.c](code/Dl/Ue/Dl_Ue_MimoDetectorLmmseEqualizer.c), [Ul_Gnb_MimoEqualizer.c](code/Ul/Gnb/Ul_Gnb_MimoEqualizer.c). Modes:

- **1×1 detector** — single-antenna MRC, output `y_eq = H* · y / (|H|² + σ²)`.
- **1×N MRC** — single-layer with N receive antennas, MRC across antennas first.
- **M×N LMMSE** — multi-layer; `y_eq = (Hᴴ·H + σ²·I)⁻¹ · Hᴴ · y`.
- **M×N ZF** — same as LMMSE with `σ² = 0` (no regularisation).

Rel-15: PDSCH up to 4 RX × 4 layers; PUSCH up to N RX × 4 layers (N gNB-impl-specific, often 4 or 8).

Outputs both the equalized symbol and a per-RE scaling factor that the demodulator uses to scale LLRs (the same `scaling[i]` we discussed in the proxy work earlier this week).

#### Layer demapper

[Dl_Ue_LayerDemapper.c](code/Dl/Ue/Dl_Ue_LayerDemapper.c), [Ul_Gnb_LayerDemapper.c](code/Ul/Gnb/Ul_Gnb_LayerDemapper.c). Inverse of the TX layer mapper: combines N layers' equalized symbols back into one codeword's symbol stream.

#### Soft demodulator

[Cn_SoftDemodulation.c](code/Common/SoftDemodulation/Cn_SoftDemodulation.c). Computes per-bit LLRs from QAM-equalized symbols. For QPSK this is a per-component scaled value; for higher-order QAM it uses the boundary method (TS 38.211 §5.1.4 inverse) with per-SC scaling factors from the equalizer.

Output range: int8 (`±127`), Q2 fixed-point.

#### Soft descrambler

[Cn_SoftDescrambler.c](code/Common/SoftDescrambler/Cn_SoftDescrambler.c). XORs the *sign* of each LLR with the same Gold PRS the TX scrambler used. Effectively a per-bit `LLR ← LLR · (1 − 2·c)` where `c` is the scrambling bit. The Gold PRS generator is the same `Cn_Prs.c` used at the TX.

#### LDPC rate de-matcher

Inverse of TX rate matcher (TS 38.212 §5.4.2):

1. **De-interleaver** (column-row, inverse of TX row-column).
2. **Circular-buffer fill** — puts each rate-matched bit's LLR back into its position in the circular buffer based on `k_0(rv)`.
3. **HARQ combining** — if this is a retransmission, sum new LLR with stored buffer LLR (clamping to int8 range), then write back to the buffer for future combining.

Output: full mother-code LLR buffer of length `N_ldpc`.

#### LDPC decoder

Layered min-sum or sum-product belief propagation on the BG1/BG2 parity check matrix. Implementations vary by vendor — refc uses fixed-point iterative decoding, typically 8-12 iterations with early termination if all parity checks pass.

Input: LLRs of length `N_ldpc`. Output: hard bits of length `K`. The first `K-24` are the info bits; the last 24 are the CB CRC. After decoding, the per-CB CRC24B is checked; if all CBs pass, the assembled TB is checked against CRC24A.

#### Polar decoder (CA-SCL)

CRC-aided successive cancellation list decoder, list size 4 or 8 (TS 38.212 §5.3.1.2 / 5.4.1).

- For PBCH: decode the 56 info+CRC bits with list size 4; CRC24C check selects the correct path.
- For PDCCH: same, but the CRC is XOR-masked with RNTI — so the decoder runs once and the post-CRC check filters out the candidates that weren't for this UE.
- For UCI ≥ 12 bits: same structure, different K/N.

#### Reed-Muller / block decoder (small UCI)

Exhaustive ML decode against the 2^K codeword set (K ≤ 11 → ≤ 2048 hypotheses) — feasible because K is so small. Used for PUCCH F2/F3/F4 with small UCI.

#### Transform deprecoder (IDFT)

[Ul_Gnb_TransformPrecoder.c](code/Ul/Gnb/Ul_Gnb_TransformPrecoder.c). Length `M_PRB · 12` IDFT per OFDM symbol after the MIMO equalizer. Only runs when `transformPrecoderFlag = 1`. Scaling `1/√N` preserves noise variance per RE.

Used on RX side: PUSCH with TP enabled, PUCCH F3/F4.

#### Pre-DFT OCC despreader (PUCCH F4)

After the IDFT in PUCCH F4 RX, the time-domain output contains the sum of `N_OCC` UEs' contributions (multiplexed by Walsh codes of length 2 or 4). The despreader correlates against the configured OCC index to extract this UE's bits.

#### HARQ buffer manager

PDSCH and PUSCH only. A per-process buffer of int8 LLRs of size `N_ldpc` (or the configured cap). New transmissions overwrite, retransmissions sum. The `newDataIndicator` flag from DCI/UCI gates between the two modes.

Per Rel-15: up to 16 HARQ processes per UE; buffer size limited by UE category.

---

## Part 4 — Cross-channel summary tables

### TX summary

| Channel | CRC | Encoder | RateMatch | Scrambler | Modulation | Layers | DMRS | DFT-spread |
|---|---|---|---|---|---|---|---|---|
| **PBCH** | 24C | Polar | Polar RM | 2-stage Gold | QPSK | 1 | Gold | no |
| **PDCCH** | 24C ⊕ RNTI | Polar | Polar RM | Gold | QPSK | 1 | Gold | no |
| **PDSCH** | 24A + 24B/CB | LDPC BG1/2 | LDPC RM (RV) | Gold | QPSK ... 256-QAM | 1-8 (≤4/CW) | Gold | no |
| **CSI-RS** | — | — | — | — | implicit QPSK | 1-32 ports | Gold | no |
| **SSB-PSS** | — | — | — | — | ZC (implicit) | 1 | — | no |
| **SSB-SSS** | — | — | — | — | m-seq (implicit) | 1 | — | no |
| **PRACH** | — | — | — | — | ZC (implicit) | 1 | — | no (own IFFT) |
| **PUCCH F0** | — | cyc-shift sel | — | — | ZC (implicit) | 1 | — | no |
| **PUCCH F1** | — | — | — | — | BPSK/QPSK | 1 | self | no |
| **PUCCH F2** | 6/11/16 | RM or Polar | block / polar RM | Gold | QPSK | 1 | Gold | no |
| **PUCCH F3** | 6/11/16 | RM or Polar | block / polar RM | Gold | π/2-BPSK or QPSK | 1 | ZC | yes |
| **PUCCH F4** | 6/11/16 | RM or Polar | block / polar RM | Gold | π/2-BPSK or QPSK | 1 | ZC | yes (with pre-OCC) |
| **PUSCH-OFDM** | 24A + 24B/CB | LDPC BG1/2 | LDPC RM | Gold | QPSK ... 256-QAM | 1-4 | Gold | no |
| **PUSCH-DFTs** | 24A + 24B/CB | LDPC BG1/2 | LDPC RM | Gold | π/2-BPSK or QPSK ... 64-QAM | 1 | ZC | yes |
| **SRS** | — | — | — | — | ZC (implicit) | 1-4 ports | — | no |

---

### RX summary

| Channel | Chest src | Equalizer | Demod | Descrambler | RateDeMatch | Decoder | CRC check | HARQ |
|---|---|---|---|---|---|---|---|---|
| **PBCH** | PBCH-DMRS | 1×1 LMMSE | QPSK | Gold (cell-ID) | Polar de-RM | CA-SCL Polar | 24C | — |
| **PDCCH** | PDCCH-DMRS | 1×1 LMMSE | QPSK | Gold (RNTI-keyed) | Polar de-RM | CA-SCL Polar | 24C ⊕ RNTI | — |
| **PDSCH** | PDSCH-DMRS | LMMSE up to 4×4 | QPSK ... 256-QAM | Gold | LDPC de-RM | LDPC BG1/2 | 24B + 24A | yes |
| **SSB-PSS** | self (xcorr) | — | — | — | — | — | — | — |
| **SSB-SSS** | self (xcorr) | — | — | — | — | — | — | — |
| **CSI-RS** | own pilots | — | — | — | — | — | — | — |
| **PRACH** | — | correlation peak | — | — | — | — | thresh | — |
| **PUCCH F0** | self (seq corr) | — | — | — | — | seq detect | thresh | — |
| **PUCCH F1** | self DMRS sym | — | BPSK/QPSK | — | OCC despread | seq detect | thresh | — |
| **PUCCH F2** | PUCCH-DMRS | 1×N LMMSE | QPSK | Gold | block / polar de-RM | block / Polar | 6/11/16 | — |
| **PUCCH F3** | PUCCH-DMRS | 1×N LMMSE | π/2-BPSK or QPSK | Gold | block / polar de-RM | block / Polar | 6/11/16 | — |
| **PUCCH F4** | PUCCH-DMRS | 1×N LMMSE | π/2-BPSK or QPSK | Gold | OCC + block/polar | block / Polar | 6/11/16 | — |
| **PUSCH-OFDM** | PUSCH-DMRS (Gold) | LMMSE up to 4×N | QPSK ... 256-QAM | Gold | LDPC de-RM | LDPC BG1/2 | 24B + 24A | yes |
| **PUSCH-DFTs** | PUSCH-DMRS (ZC) | LMMSE 1×N + IDFT | π/2-BPSK ... 64-QAM | Gold | LDPC de-RM | LDPC BG1/2 | 24B + 24A | yes |
| **SRS** | own seq | — | — | — | — | — | — | — |

---

## How to read this

If you want to understand a channel end-to-end, follow its **TX chain in Part 1** and its **RX chain in Part 2** top-to-bottom (RX is essentially TX in reverse, with some asymmetric blocks like the blind decoder and HARQ combiner). Then look up each named block in **Part 3** — shared components (LDPC, polar, CRC, Gold PRS, modulator, channel estimator, MIMO equalizer, soft demod, …) are described **once** in Part 3 and reused by reference in the chains.

If you want to compare two channels (e.g. PDSCH vs PUSCH, or PUCCH F2 vs F3), the **Part 4 tables** are the fast comparator — every column is one design decision. There are two tables: one for TX, one for RX, with the same row order so you can read across.

If you're tracking down where a specific 3GPP feature lives in the refc code, the clickable links in Part 1 / Part 2 take you straight to the driver function.
