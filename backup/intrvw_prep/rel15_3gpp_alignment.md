# Chandan Bangalore — CV Alignment with 3GPP Release 15 Specifications

> Specifications covered: TS 38.211, 38.212, 38.213, 38.214, 38.104, 38.141

---

## TS 38.211 — Physical Channels and Modulation

**Alignment: ★★★★★**

This spec defines the waveform, physical channels, reference signals, and modulation schemes for NR.

Alignment is deep and direct. The full NR PHY pipeline has been implemented — PDSCH, PDCCH, PUSCH, PUCCH, SRS, PRACH — covering resource mapping, modulation, OFDM waveform generation, and reference signal design as defined in 38.211. MIMO-OFDM work and channel estimation modules also map directly here.

**Key evidence from CV:**
- Designed and implemented NR UE PHY transmitter (PUCCH/PUSCH) and receiver (PDCCH/PDSCH) pipeline, including modulation, resource mapping, and waveform generation
- MIMO-OFDM channel estimation for uplink receiver in multipath fading environments (Master Thesis)
- SSB, PDSCH, PDCCH, PUSCH, PUCCH, SRS, PRACH listed as core PHY layer skills

---

## TS 38.212 — Multiplexing and Channel Coding

**Alignment: ★★★★★**

This spec covers LDPC (data channels), Polar codes (control channels), rate matching, and bit-level multiplexing.

Alignment is hands-on and thorough. LDPC and Polar encoders/decoders were implemented from internship through master thesis, explicitly citing Release 15 compliance. Data/control multiplexing and demultiplexing modules were also developed — core 38.212 material.

**Key evidence from CV:**
- Implemented LDPC encoder (data channel) and Polar encoder (control channel) per 3GPP NR Release 15 (Internship)
- Implemented channel decoding algorithms for LDPC decoder and Polar decoder per 3GPP Release 15 (Master Thesis)
- Developed data and control multiplexing/demultiplexing modules for NR PHY transmitter chain

---

## TS 38.213 — Physical Layer Procedures for Control

**Alignment: ★★★★☆**

This spec defines how the UE determines transmission parameters, including PDCCH decoding, DCI formats, power control, and scheduling decisions.

Alignment is solid. PDCCH receiver pipeline implementation and L1-L2 FAPI/nFAPI interface work (slot-level scheduling, P7 data-plane messages) directly touches procedures defined in 38.213.

**Key evidence from CV:**
- PDCCH receiver pipeline design and implementation
- Developed L1-L2 interface layer compliant with SCF 5G nFAPI/FAPI (v15.1), implementing P5 (config/control) and P7 (data-plane) message parsers for slot-level scheduling
- Control channel processing is a consistent thread across multiple roles

---

## TS 38.214 — Physical Layer Procedures for Data

**Alignment: ★★★★☆**

This spec covers link adaptation, HARQ, CSI reporting, PDSCH/PUSCH resource allocation, TBS and MCS selection.

Alignment is strong. PDSCH/PUSCH pipeline design, MIMO configurations, channel estimation, and equalization are all core to 38.214 procedures. Receiver performance evaluation (BER, throughput) across 3GPP channel models in the master thesis also maps here.

**Key evidence from CV:**
- PDSCH/PUSCH pipeline design and implementation
- Developed channel estimation, parameter estimation, and equalizer modules for single and multiple antenna (MIMO) configurations
- Evaluated receiver performance in terms of BER and throughput across multiple 3GPP channel models (Master Thesis)

---

## TS 38.104 — Base Station (gNB) Radio Transmission and Reception

**Alignment: ★★★★★**

This spec defines RF requirements for gNB: frequency bands, output power, ACLR, EVM, reference sensitivity, and spurious emissions.

Alignment is practical and measurable. MATLAB testbenches were explicitly developed to verify ACLR and EVM conformance metrics, and RF testing was performed using Keysight X-Series Signal Analysers and Signal Studio Pro — all directly targeting 38.104 conformance for FR1 and FR2 bands.

**Key evidence from CV:**
- Developed MATLAB simulation testbenches to verify 3GPP conformance metrics including ACLR and EVM for target PAPR values
- Performed RF testing and validation using Keysight/Agilent X-Series Signal Analyser and Signal Studio Pro (5G NR)
- FR1 & FR2 listed as core 3GPP/Standards skills

---

## TS 38.141 — Base Station Conformance Testing

**Alignment: ★★★★★**

Implemented and validated NR PHY receiver demodulation performance per TS 38.141, verifying PDSCH/PUSCH throughput targets (70%/95% of maximum) across 3GPP fading channel models (AWGN, CDL, TDL, EPA, EVA, ETU) at defined SNR operating points for both SISO and MIMO antenna configurations.

**Key evidence from CV:**
- "Designed and developed 3GPP NR communication protocol stack (Release 15) per TS 38.211/212/213/214, implementing and conformance testing all uplink and downlink physical channels per TS 38.104/141 for FR1 and FR2 bands" (Design Engineer, CommAgility)

---

## Summary Table

| Specification | Topic | Alignment | Key Strength |
|---|---|---|---|
| TS 38.211 | Physical Channels & Modulation | ★★★★★ | Full channel pipeline, OFDM, resource mapping, reference signals |
| TS 38.212 | Multiplexing & Channel Coding | ★★★★★ | LDPC/Polar encode/decode, mux/demux modules |
| TS 38.213 | Physical Layer Procedures for Control | ★★★★☆ | PDCCH pipeline, FAPI scheduling interface |
| TS 38.214 | Physical Layer Procedures for Data | ★★★★☆ | PDSCH/PUSCH, MIMO, channel estimation, BER/throughput |
| TS 38.104 | gNB Radio TX/RX Requirements | ★★★★★ | ACLR/EVM testing, FR1/FR2 RF validation, Keysight tools |
| TS 38.141 | gNB Conformance Testing | ★★★★★ | Explicit conformance testing across UL/DL channels |

---

## Overall Assessment

The CV demonstrates exceptionally strong and direct alignment with all six specifications. The career progression from intern → master thesis → design engineer → senior engineer tells a coherent story of growing ownership over NR PHY implementation and conformance testing. The combination of hands-on implementation (38.211/212), procedure-level understanding (38.213/214), and RF/conformance validation (38.104/141) is rare and highly valuable for roles in 5G NR PHY development.

---

*Generated from CV analysis — Chandan Bangalore | May 2026*
