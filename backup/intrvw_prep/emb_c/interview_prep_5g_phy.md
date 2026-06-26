# Senior 5G NR PHY Interview — Prep Notes

Grounded in `~/workspace/refc` (gNB PHY) and `~/workspace/nr_ue_phy` (UE PHY).

---

## Q1 — Platform-specific code & cross-compilation

### How `#ifdef` is used

Two layers of platform abstraction, deliberately:

1. **`src/` is platform-agnostic.** No SIMD intrinsics, no `#ifdef X86` ladders inside business logic. Algorithmic code calls a stable `cn_*` API (`cn_ldpc_decoder`, `cn_demodulation`, `cn_chest`, `cn_crc24a`). This is enforced — `src/dl/README.md` explicitly forbids intrinsics there.

2. **`lib/` carries the platform split.** Same `cn_*` symbol, two implementations:
   - `lib/x86/` → AVX2 (`_mm256_madd_epi16`, `_mm256_packs_epi32`, ~580 intrinsic call sites).
   - `lib/platform/arm_ran/` → NEON (`vld2q_f32`, `vmlaq_f32`, `vqmovn_s32`, ~150 sites) plus calls into ARM's RAN Acceleration Library for the heavy stuff (LDPC, FFT).

CMake picks one or the other:
```cmake
if (PLATFORM STREQUAL "x86")
    add_subdirectory(platform/intel_ipp)
    add_subdirectory(x86)
else ()
    add_subdirectory(platform/arm_ran)
endif()
```
`src/` links against whichever was selected — same headers, different implementation.

### Toolchain file mechanics

`toolchains/startag-1.1.0.cmake` does:
```cmake
set(CMAKE_SYSTEM_NAME Linux)
set(CMAKE_SYSTEM_PROCESSOR arm)
set(CMAKE_C_COMPILER aarch64-linux-gnu-gcc)
set(CMAKE_SYSROOT $ENV{HOME}/nxp_tools/sysroot_startag-...)
set(PLATFORM "arm")
set(RFHW_STARTAG_110 ON)
set(PLATFORM_PACKAGE_NAME startag_hw_1.1.0)
```
The toolchain establishes the cross-compiler triple, the sysroot for headers/libraries, the **target identity** (`PLATFORM`, `RFHW_*`), and a packaging name used downstream by `make package`. There's also `startag-noRF.cmake` which **forces** `NMM_RF_ACTIVE=Off` with a fatal error if you try to override — that prevented a class of "tried to build for HW but RF stack was wired in" mistakes.

### Macros that drive code paths

(passed via `target_compile_definitions` / `-D` from top CMakeLists)

| Macro | Source | Effect |
|---|---|---|
| `X86` / `PLATFORM_X86` / `PLATFORM_ARM` | top CMakeLists by `PLATFORM` | High-level platform branch |
| `RF_ACTIVE` | set when `NMM_RF_ACTIVE=On` on ARM | Pulls in real LA9310 RF, M4 firmware externalproject, multi-core scheduler |
| `RFHW_STARTAG_110` / `RFHW_NXPRDB1` | toolchain | Per-board calibration & DFE init |
| `MULTI_CORE` | implied by `RF_ACTIVE` | Activates real cross-core ICM via `BSP_IPC_sendICM_Message` |
| `NO_REALTIME` | x86 only | Skips `SCHED_FIFO`, falls back to `SCHED_OTHER` (you can't rely on real-time scheduling on a dev box without root + cgroups) |
| `NMM_FREQ_RANGE_FR2` → `FREQ_RANGE` | option | FR1/FR2 numerology tables, SSB Case A–E selection |
| `HARQ_DEBUG_DUMP_EN`, `UL_DEBUG_DUMP_FLAG` | optional | Compile-in dump points for offline analysis — zero cost in production |
| `USE_ASAN` | debug only | `-fsanitize=address -fno-omit-frame-pointer`; we run our component CTests under ASAN regularly |

### Clean structure rules

- Don't `#ifdef` inside hot loops — ever. If a function diverges, give it two implementations behind one symbol in `lib/`.
- The OS layer (`lib/os/wrp_*`) has its own platform split (`lib/os/linux/osal/` vs the NXP variant). That keeps pthread-vs-FreeRTOS leakage out of PHY code. The DFE library cross-compiles separately for the LA9310 Cortex-M4 as `la9310_rflib`.
- ARM build adds `-Wno-error=sign-compare` because the ARMRAL headers trip it; rather than litter the code with casts, scope the relaxation to the platform that needs it.

---

## Q2 — Slot-wise vs symbol-wise processing

**Short answer: slot-wise, with one symbol-level handoff at the FFT boundary, and `SLOT_IND_ADVANCE` lookahead.**

### What our threads see

- `trd_pdsch`, `trd_pdcch`, `trd_sync`, `trd_ulcomp` all wake on per-slot ICM messages. The trigger is `INTERCOMP_MSG_ID_L1C_SLOT_IND` from L1C, originated from the DFE's slot tick.
- The slot indication arrives **in advance** — `SLOT_IND_ADVANCE = 2` slots in `RF_ACTIVE` mode and `1` slot in simulation (`toplevel/phy/trd_l1c.c`). This is the key latency-hiding mechanism: PHY gets DL_CONFIG/UL_CONFIG before the airtime arrives.
- Symbol-level work happens **inside** these threads. `dl_pdsch_process()` in `src/dl/pdsch/dl_pdsch.c` (lines ~299–648) loops symbol-by-symbol for CFO comp, pilot extract, equalization, demod — but the thread is still slot-driven.

### Pros / cons

| | Slot-wise (what we do) | Symbol-wise pipelining |
|---|---|---|
| Latency | Worst-case = 1 slot | Symbol granularity (~36 µs at 30 kHz SCS) |
| Throughput | Easier to batch SIMD across all 14 symbols of a TB | Better for L4S / URLLC where you need to start LDPC before all symbols land |
| Code complexity | Linear, debuggable | Requires per-symbol state machines, partial soft-buffer accumulation |
| HARQ combining | Done once per TB | Would need per-symbol partial combining or buffering anyway |
| Memory pressure | Whole-slot buffers (115200 B per HARQ proc × 16) | Smaller working set |

### Why we picked slot-wise

- UE is bursty by nature (DRX, infrequent grants for many UEs). Throughput-on-grant matters more than per-symbol latency.
- LDPC and rate recovery operate on the whole rate-matched block — doing them symbol-wise saves ~0 because the decoder needs the full E bits anyway.
- The DFE owns OFDM demod (per-symbol FFT inside the LA9310 VSPA), so by the time the ANT data hits `INTERCOMP_MSG_ID_PDSCH_BASEBAND_DATA`, it's already FFT'd and packaged as `nr_cf32_t dlFftAntennaData[ANT][SYMBOL]`. We don't *gain* anything by re-pipelining at the C level.

### Where we *do* pipeline symbol-wise

- DMRS handling: PDSCH does CHEST on the DMRS symbol *immediately* and starts equalizing the next data symbol while waiting for further DMRS. The `intermediateDataIndicationSymb` field in `DlPdsch_DataIndIcmBody` is exactly this hook — DFE tells PDSCH "symbols up to N are ready" so we can begin partial work mid-slot.
- Sync: PSS is correlated continuously over a sliding window — that's stream processing, not slot processing, because you don't yet know where slot boundaries are.

For a gNB doing massive MIMO with strict TDD turnaround, you'd flip more aggressively to per-symbol pipelining. The reference `~/workspace/refc` doesn't — it's a reference simulator where one `Dl_Gnb_Transmitter_processData()` call processes one slot synchronously.

---

## Q3 — Inter-process / inter-core / inter-thread communication

Three layers, each with a purpose.

### 1. Inter-process: PHY ↔ MAC over UDP

`uephy` and `macemu` are separate processes. `trd_l1c_rx` opens a UDP socket on `PHY_IF_UE_PHY_UDP_PORT = 12378` (`inc/phyifue.h`) and demuxes by `PhyIfUe_MsgType`:

| Direction | Message | Purpose |
|---|---|---|
| MAC→PHY | `CONFIG_REQUEST` (0x02) | Cell config (one-shot) |
| MAC→PHY | `DL_CONFIG_REQUEST` (0x80) | Per-slot DL grant |
| MAC→PHY | `UL_CONFIG_REQUEST` (0x81) | Per-slot UL grant |
| PHY→MAC | `DCI_INDICATION` (0xa2) | Decoded DCIs |
| PHY→MAC | `DL_DATA_INDICATION` (0xa3) | Decoded TBs + HARQ ACK/NACK |
| PHY→MAC | `MEAS_INDICATION` (0xa6) | RSRP/RSRQ |

Wire format is a 5-byte header (`uint8_t messageTypeID + uint32_t messageBodyLength`) followed by the typed body. UDP because (a) MAC and PHY can be on different boards, (b) it's friendlier to a Wireshark dissector than shared memory.

### 2. Inter-core: ICM via shared memory + IPC mailbox

On StarTag with `MULTI_CORE`, `BSP_IPC_sendICM_Message` (in NXP BSP) shovels an InterCompMessageSharedStruct between A53 cores. The DFE-side runs on the LA9310 Cortex-M4 plus VSPA DSP — those communicate with the A53 over hardware mailboxes via `dfe_if_*` ICM messages (e.g. `INTERCOMP_MSG_ID_DFE_AL_SLOT_CONFIG`).

### 3. Inter-thread: WRP message queues + skeleton macros

Each thread (component) owns one `WRP_MsgQueue` with **4 weighted sub-queues**:

```c
// lib/skeleton/skeleton_macros.h
DATA (0)            // baseband data — highest cadence
FRAME_HANDLER (1)   // per-slot config
CONTROL (2)         // start/stop/destroy
TIMER (3)
```

Senders go through `SKL_POST_MESSAGE(msg, sendingMethod)` with three delivery modes:
- `WRP_BUFFERED` — enqueue + `sem_post` the owner; standard async.
- `WRP_UNBUFFERED` — direct handler call in sender's context. Used for tight, cheap, lock-free traversals.
- `WRP_LATE_BUFFERED` — enqueue without signaling. Used to coalesce a group of messages before letting the receiver wake.

Allocation is from per-thread buffer pools (`SKL_ALLOC_INTERCOMP_MESSAGE`), not malloc, to keep the slot-loop free of allocator jitter.

### Sync primitives (`lib/os/wrp_*`)

- `WRP_MUTEX` over `pthread_mutex_t` — used for buffer-pool free-lists and config double-buffers.
- `WRP_Semaphore` — every task has one, that's how the message queue wakes it (counting semaphore = how many messages pending).
- `pthread_cond_t` inside `WRP_Task` — for suspend/resume.
- `itc_shared_msg_t` (`lib/mt/itc.h`) — alternate path with mutex+cond for paths where queue overhead isn't justified.

### Avoiding races

- **Single-writer rule on big buffers.** `dlFftAntennaData[ANT][SYMBOL]` is filled by DFE, then the buffer pointer is *handed off* via ICM. Once PDSCH receives the data-ind, DFE will not touch that buffer again until PDSCH calls `TrdDlPdsch_releaseBuffers()`. Ownership is implicit but enforced by code review.
- **Slot-advance lookahead** means the DFE-side TX buffer for slot N is being filled by ULCOMP while the DFE is still transmitting slot N−1. Two buffers ping-pong; we never need a lock on the active one.
- **Double-buffered config.** The MAC sends DL_CONFIG for slot N+2 while PDSCH is decoding slot N. L1C copies the immutable parts and queues the per-slot config indexed by slot number — no in-place mutation.
- **Per-process HARQ state** (16 processes per TB, `dl_harq.c`) — only `trd_pdsch` ever touches `hram_start[]`. MAC's NDI/RV come in via DL_CONFIG. No locks needed because there's exactly one writer.

---

## Q4 — Data transfer, buffer management & config handling

### IQ samples (RX path)

1. **DFE owns the time-domain ADC pipeline.** ADC → decimation → 30.72 MHz. DFE then performs CP removal + FFT *inside the LA9310 VSPA* (not on the A53). Output is `nr_cf32_t dlFftAntennaData[ANT][SYM]`.
2. Buffer is allocated by DFE from `SKL_BUF_POOL_DL_ANT_DATA_BUFFER` (`toplevel/phy/phy_skeleton.h`). Pool is sized at init: `numBuffers × sizeof(slot worth of FFT'd samples)` where each symbol is `numRB × 12 × sizeof(nr_cf32_t)`.
3. DFE posts `INTERCOMP_MSG_ID_PDSCH_BASEBAND_DATA` (or `..._PDCCH_...`) carrying **pointers**, not copies. PDSCH decodes, then calls release-to-pool.
4. `intermediateDataIndicationSymb` field lets DFE post the data-ind early ("symbols 0..N ready") for pipelined work.

### Decoded bits (RX → MAC)

PDSCH writes the decoded TB into a `PhyIfUe_DlIndicationAndData` and sends it over UDP via `WRP_Socket_udpSendTo`. MAC then owns the TB buffer.

### TX (UL)

`trd_ulcomp` allocates from `SKL_BUF_POOL_UL_ANT_DATA_FFT_BUFFER` (frequency-domain) or `SKL_BUF_POOL_UL_ANT_DATA_PRACH_BUFFER` (time-domain ZC). Posts `INTERCOMP_MSG_ID_DFE_AL_SLOT_CONFIG` to DFE; DFE does IFFT+CP add+DAC.

### Buffer sizing (real numbers)

- HARQ soft buffer: `DL_HARQ_HRAM_PER_PROC_SIZE = 115200` bytes per process × 16 processes = ~1.84 MB total. Sized for max TB at peak rate. Plus a separate 19200-byte broadcast/QPSK buffer for SI-RNTI.
- DL ant data: `UE_PHY_MAX_NUM_ANT × UE_PHY_MAX_NUM_SYMBOLS × max_RB × 12 × 8B` (cf32) — roughly 9 MB at 100 MHz × 4 ant.
- Pool depths: typically 4–8 buffers per pool — enough to cover `SLOT_IND_ADVANCE` plus retx jitter without backpressure.

### Config flow

- `CONFIG_REQUEST` arrives once at session start, distributed via L1C to all components as `INTERCOMP_MSG_ID_*_CONFIG_REQ`. Stored statically per component.
- `DL_CONFIG_REQUEST` / `UL_CONFIG_REQUEST` are **per slot**, identified by SFN+slot. L1C queues them indexed by `slot mod N`. PDSCH/PDCCH/ULCOMP read the config at the matching slot indication.
- **Config is read-only after enqueue.** PHY does not write into MAC's config struct.

### What if a buffer overflows or config is late?

- **Pool exhaustion**: `SKL_ALLOC_INTERCOMP_MESSAGE` returns NULL. We log `LOG_EXCEPTION` and drop. In practice we tune pool depths during integration so this never fires under spec'd load.
- **Late config**: if DL_CONFIG for slot N arrives after slot-ind for N has already been dispatched, that slot's PDSCH gets no work — we mute it. The MAC sees no `DL_DATA_INDICATION` and treats it as NACK on its retx logic. This was a real failure mode early on — we added a "config-arrival deadline" check in L1C, and a counter that the MAC can poll.
- **TB CRC fail**: HARQ keeps the soft buffer alive (NDI not toggled), waits for the gNB to retransmit with a new RV, and combines on next reception (`dl_harq_soft_comb` in `dl_harq.c`).

---

## Q5 — Messages and data between threads

Walk the slot lifecycle; this is what actually moves on the wire.

### Slot N timeline

1. **DFE → L1C**: `INTERCOMP_MSG_ID_L1C_SLOT_IND` (`TrdL1C_slotIndication { slot, sfn, seqNumber }`). Tiny, cadenced at slot-rate.
2. **L1C → PDCCH/PDSCH/ULCOMP**: forwards slot indication + the matching `DL_CONFIG` / `UL_CONFIG` (carried inside `*_DlConfigRequestIcm` structs that hold pointers to the MAC's `PhyIfUe_DlConfigRequest`).
3. **DFE → PDCCH**: `INTERCOMP_MSG_ID_PDCCH_BASEBAND_DATA` carrying `DlPdcch_DataIndIcm`:
   ```c
   nr_cf32_t *dlFftAntennaData[MAX_ANT][MAX_SYMBOLS];   // pointers
   uint32_t  seqNumber, numSymbols;
   nr_ci16_t *timeDomainBuffer, *freqDomainBuffer;
   ```
   PDCCH does blind decode, posts decoded DCIs.
4. **PDCCH → PDSCH**: decoded DCIs flow through L1C as part of the next DL config (so the DCI for slot N typically schedules slot N+k).
5. **DFE → PDSCH**: `INTERCOMP_MSG_ID_PDSCH_BASEBAND_DATA` (`DlPdsch_DataIndIcm`, similar layout).
6. **PDSCH → MAC** (over UDP): `DL_DATA_INDICATION (0xa3)` with TB bytes + HARQ-ACK status.
7. **MAC → PHY**: `UL_CONFIG_REQUEST (0x81)` with PUSCH/PUCCH/PRACH PDUs.
8. **L1C → ULCOMP**: `INTERCOMP_MSG_ID_ULCOMP_UL_CONFIG_REQ`. ULCOMP runs `ul_pusch_process` / `ul_pucch_process` / `ul_prach_ShortFormats_processData`.
9. **ULCOMP → DFE**: `INTERCOMP_MSG_ID_DFE_AL_SLOT_CONFIG` (`DfeIf_SlotConfigRequestIcm`) with FD samples per `[ANT][SYM]` plus PRACH TD samples.

### Data sizes per stage

- ICM control msgs: typically 32–256 bytes (mostly headers + pointers).
- Data ICM: ~24 B header + pointer arrays (real data lives in shared pools).
- TB on UDP to MAC: actual TB size, e.g. 8424 bits = ~1 KB for an MCS22 single-CB.
- DL config from MAC: scales with PDU count, typically a few KB per slot.

### Format

Every ICM message has `InterCompMessageSharedStruct` first member:
```c
{ senderComponent, destinationComponent, messageID, messageSize }
```
This is what `SKL_POST_MESSAGE` reads to route — same model whether intra-thread, inter-thread, or inter-core.

### Thread safety on data passing

- **Pointer handoff with implicit ownership** — described in Q3. Buffer is inside a pool; handing off a pointer transfers responsibility to release.
- **Sequence numbers** (`seqNumber` field on every data ICM) — receiver checks monotonic ordering. We've caught DFE→PDSCH races where two seq numbers landed out of order due to a missed mutex; the seq check fired an `LOG_EXCEPTION` and made the bug obvious.
- **Sub-queue priority** ensures `DATA` doesn't starve `CONTROL` — STOP requests never get queued behind a backlog of slot data.
- **No shared mutable state** between PDSCH and ULCOMP. They read different parts of the slot config; configs are immutable after enqueue.

---

## Q6 — Symbol pipeline & latency hiding (DMRS sym-2 → sym-7)

**Mapping Type A**, l_d=12, dmrsAddPos=1: DMRS at symbols {2, 7} (or {0,7} for some configs — see the lookup table at `src/dl/pdsch/dl_pdsch.c:71-130`, mapping TS 38.211 Table 7.4.1.1.2-3).

### What sym 3, 4, 5, 6 do

They are **data symbols**. Two parallel things are happening:

**A. CHEST on sym-2 finishes, then equalization can begin on sym-3 immediately.**

In `dl_pdsch_process()`:
1. Pilot extract on sym-2 → LS estimate per RE (`cn_chest`).
2. Frequency averaging within each RB (`cn_chest_freq_avg`) — smooths the LS noise.
3. **First-pass CFO estimation** uses sym-2 alone or sym-2+sym-7 if available; we apply CFO comp to the input data buffer (`cn_cfoComp`).
4. Compute regularization (MMSE or MMSE-IRC) and copy/scale the channel estimate to the data symbols (`cn_chest_scaling` / `cn_chest_scaling_irc`).
5. **Equalize sym-3 → sym-6** with the sym-2 channel estimate, and also sym-8…11 with sym-7 (or interpolated).
6. Soft-demap to LLRs (`cn_demodulation`), descramble.

**B. The DFE keeps delivering symbols.**

While the PHY is processing sym-2's CHEST, sym-3..6 ANT data is being FFT'd and DMA'd into the FD buffer. The `intermediateDataIndicationSymb` field tells PDSCH "you can start working on these N symbols now."

### Pipeline structure for hiding the gap

```
DFE timeline:    [sym2 FFT][sym3 FFT][sym4 FFT][sym5 FFT][sym6 FFT][sym7 FFT]...
PDSCH timeline:           [DMRS extract][CHEST][EQ sym3-6 in parallel       ][CHEST sym7][EQ 8-11]
```

Sym 3–6 don't sit idle. Their FFT'd samples land in the buffer pool, and PDSCH equalizes them as soon as the sym-2 channel estimate is ready. Demod and descramble run as a tight loop over data symbols. The bottleneck isn't the gap between DMRS — it's the LDPC decode at the end.

### CHEST interpolation across the slot

Honestly: in our code, **time-direction is a flat copy, not a true linear or sinc interpolation**. After `cn_chest_time_avg` averages multiple DMRS symbols, the result is broadcast to all data symbol positions via `cn_chest_scaling(..., COPY_1_TIMES, ...)` (see `dl_pdsch.c:528-529`). Frequency-direction has the freq-average smoother.

That works fine when Doppler is low and dmrsAddPos provides 2+ DMRS symbols (you average across them, which is implicit time interpolation at zero order). It breaks when:
- High mobility (Doppler > ~5% of SCS) — phase rotates measurably between DMRS occasions.
- Single DMRS symbol per slot (dmrsAddPos=0).

**This is a known deviation from textbook MMSE-Wiener interpolation** — and one of the things to call out as a tuning opportunity if optimizing for high-speed scenarios. The gNB side (`refc/.../Ul_Gnb_ChannelEstimator.h`) actually does makima (modified Akima) interpolation in frequency and a Wiener filter in time. We didn't bring that to the UE because the runtime cost is significant and the SNR gain is small at our typical operating points.

### CFO refinement

After the first equalize/demod pass, we do a second CFO estimate using *all* DMRS symbols (`cn_cfoEstimation` uses dmrsSymIndex array), apply that to the input, re-extract pilots, re-do CHEST. This is in `dl_pdsch.c:452-485`. It's the closest we get to symbol-level pipeline refinement — and it specifically exists because between sym-2 and sym-11, even a few hundred Hz of CFO drift wrecks the constellation.

---

## Q7 — Real problems encountered

Three concrete ones from this codebase, all on branch `engineering/NRUEL1-1410` and recent history.

### Problem 1 — ULP scaling broke higher-order MCS

**Symptom**: PDSCH BLER was fine for QPSK and pretty bad for 16QAM/64QAM at moderate SNR (~14 dB). Reproduced cleanly on a TV with MCS17.

**Identified by**: `scripts/run_x86_regression.sh` against the standard TV directory — the BLER table on the dashboard (the Python `dashboard.py` at port 5050) was green for QPSK rows and red for 16QAM. CTest at component level hadn't caught it because the unit test for `cn_demodulation` used a fixed scale factor that didn't hit the regression.

**Root cause**: the demodulator's ULP (unified log-probability) threshold was tuned per-modulation. For 16QAM and above, the LLRs were saturating prematurely at the int8 boundary because the equalizer scaling for MMSE-IRC produced different magnitudes than scalar MMSE. The QAM16+ branch used `DEMOD_ULP_ARM_RAL_QAM16_OR_HIGHER = 512` while the eq output was scaled assuming a different range.

**Fix**: re-derived ULP per equalizer mode, added scaling-aware paths in `dl_pdsch.c` and a NEON-specific scaling macro on the ARM side. The recent commits `ce35a4d5` (NEON scaling macros, ZF scaled per EQ type) and `89e9aaa4` (master version of ULP for non-QPSK) are this work.

**Lesson**: unit tests for soft-output blocks need to span the actual equalizer dynamic range, not a synthetic one. Added per-mod, per-eq test points to the `cn_demodulation` CTest.

### Problem 2 — HARQ soft combining mis-locked NDI on RV2 retransmissions

**Symptom**: Throughput collapse when retx happened. Looked like soft buffer was being thrown away on what should have been a combine.

**Identified by**: `HARQ_DEBUG_DUMP_EN=1` build dumped the per-process soft buffer pre/post combine. Diff showed the buffer being zeroed on retx instead of summed.

**Root cause**: the NDI toggle check used the previous DCI's NDI from a different harqProcessID slot due to a stale index in `Dl_LatestInfo_s`. So a *new* TB on process 4 looked like a *toggle* against process 3's last NDI, and the soft buffer was correctly thrown away — but a *retx* on process 3 sometimes tested against a stale value too and got marked as new.

**Fix**: indexed `Dl_LatestInfo_s` strictly by `harqProcessID` and validated NDI compare per process. Added a CTest with synthesized RV0→RV2 sequences across all 16 processes interleaved.

**Lesson**: HARQ state per process must be hermetic. Don't share "latest seen" trackers across processes.

### Problem 3 — Slot-config arrival jitter caused PRACH preambles to miss occasions

**Symptom**: random RACH failures during integration. PRACH preamble being computed and queued, but the DFE TX'd a zero-IQ slot. Looked like 5–10% miss rate.

**Identified by**: Wireshark on the macemu↔uephy UDP link timestamped each `UL_CONFIG_REQUEST`; correlation with `LOG_EXCEPTION` lines in uephy showed config arriving *after* SLOT_IND for that slot in 5% of cases. This happened because the macemu was running on the same machine as uephy under load, and Linux scheduling jitter > our `SLOT_IND_ADVANCE = 1` slot in simulation mode.

**Root cause**: not a PHY bug per se — it was a timing assumption. With one slot of advance, any scheduling hiccup > 500 µs (sim slot duration at 30 kHz SCS = 500 µs) lost the slot.

**Fix**: bumped `SLOT_IND_ADVANCE` to 2 in simulation mode for stress runs; set CPU pinning on the test rig (`taskset` to specific cores); added a "config-late" counter exposed via `MEAS_INDICATION` so we can observe the rate from the test harness.

**Lesson**: lookahead is your only defense against jitter, and "1 slot ahead" is not enough on a non-RT host. On real hardware with `SCHED_FIFO` and `MULTI_CORE` defined, this was never an issue.

---

## Q8 — Full PHY architecture

### gNB PHY (`~/workspace/refc`)

**TX (DL)** — `Dl_Gnb_Transmitter_processData()`:
```
Per PDSCH PDU:
    TB → CRC24A → CB segmentation → per-CB CRC24B
       → LDPC encode (BG1 if tbSize>3824 OR coderate>2/3, else BG2)
       → rate matcher (RV/k0 lookup, bit selection, bit interleaving, qM packing)
       → scramble (PRS seeded by RNTI<<15 + nID)
       → modulate (QPSK..256QAM)
       → layer mapper (1->2->4->8 layers per TS 38.211 7.3.1.3)
       → DMRS+PT-RS gen+map (per antenna ports 1000..1010)
       → PDSCH resource mapper (RB grid)
       → precoder per PRG (PMI-driven W matrix)
       → digital precoder (TXRU mapping)

Per PDCCH PDU:
    DCI fields → DCI encoder → CRC24C → Polar encode → Polar rate match
       → QPSK → CCE->REG mapping → CORESET RB write

SSB (every 20 ms): PSS/SSS gen → PBCH BIT process (CRC24C+Polar) → PBCH-DMRS → SSB mapper → port 4000

CSI-RS: pattern gen → port 3000+

Aggregate: Baseband composes the slot grid (PDSCH+PDCCH+SSB+CSI-RS+DMRS)
       → IFFT (Cn_Fft) → CP insertion (Dl_Gnb_CpInsertion)
       → IComplex16 time samples per antenna
```

**RX (UL)** — `Ul_Gnb_Receiver_processData()`:
```
Time samples → CP removal → FFT → frequency grid

Per PUSCH PDU:
    DMRS extract → channel estimation (makima freq + Wiener time)
       → CFO estimation (Xcor or Fbin variants)
       → MIMO equalizer (SISO / MRC / LMMSE picked by config)
       → layer demap → optional transform precoding removal
       → soft demod (Cn_SoftDemodulation_*)
       → descramble (soft, sign-flip)
       → LDPC rate dematch with HARQ accumulation (Cn_LdpcRateDematcherHarq)
       → LDPC decode (belief propagation)
       → CRC24B per CB → CB collect → CRC24A on TB
       → output: TB bytes + HARQ-ACK status

PUCCH: format 0/1/2/3/4 specific demod → polar decode UCI → ACK/SR/CSI
PRACH: baseband FFT → ZC correlator → peak detect → preamble ID, TA
SRS:  reference correlation → channel estimate → CQI measurement
```

**gNB threading**: synchronous slot-by-slot, single-threaded entry point. `processData()` cascades through every component within one TTI. Memory pre-allocated, no malloc on the hot path. The reference is meant to be deterministic and golden-vector-checkable, not throughput-optimized.

### UE PHY (`~/workspace/nr_ue_phy`)

**RX (DL)** — distributed across `trd_sync`, `trd_pdcch`, `trd_pdsch`:

```
trd_sync (cell search):
    PSS time-domain → freq-domain FIRC correlation
       (5 CFO hypotheses {-1, -0.5, 0, +0.5, +1} x SCS, 3 NID2 candidates)
       → top-4 candidates with peak_pos, c_cfo, f_cfo
    SSS at sym+13 from PSS → cell_id (NID1*3 + NID2)
    PBCH: extract → MMSE eq → polar decode → MIB
    Output: cell_id, ssb_index, frame_start, RSRP/RSRQ/SNR

trd_pdcch:
    For each search space x aggregation level x candidate position:
        DMRS extract → CHEST (LS + freq smooth)
        EQ (ZF or MMSE per config)
        QPSK soft demod → descramble (RNTI<<15 + scramId)
        Polar rate dematch → polar decode → CRC24
        if CRC OK: parse DCI by format (1_0/1_1/0_0/0_1/...)
    Output: list of decoded DCIs per RNTI

trd_pdsch:
    DMRS gen (cn_prs_gen seeded per TS 38.211 7.4.1.1.2)
       → pilot extract per CDM group → LS CHEST
       → freq avg + time avg across DMRS symbols
       → CFO est+comp, then re-est for refinement
       → MMSE/MMSE-IRC regularization → scale to data symbols
       → per-symbol equalize → soft demod (adaptive ULP per qM)
       → descramble (RNTI<<15 + dataScramblingId)
       → HARQ soft combine (NDI toggle decides discard vs sum)
       → LDPC rate recovery (RV-aware k0, puncture/repeat unwind)
       → LDPC decode (BG1/BG2)
       → CRC24A (TB > 3824) or CRC16 (else)
    Output: TB bytes, HARQ-ACK
```

**TX (UL)** — `trd_ulcomp`:

```
Per PDU in UL_CONFIG:
    PUSCH:
        TB → CRC24A → CB segmentation → CRC24B → LDPC encode (BG1/BG2)
           → rate match → scramble → modulate (QPSK..256QAM)
           → DMRS gen+map (or short-seq for DFT-s-OFDM)
           → optional transform precoding (DFT per symbol for pi/2-BPSK)
           → resource mapping per [ant][sym]
    PUCCH (format 0/1/2/3/4):
        ACK/SR bits → 1-bit / 2-bit / block encoder
        cyclic shift (initial m0 + mcs(payload))
        group/seq hopping (PRS-based per TS 38.211 6.3.2.2.1)
        spreading + map
    PRACH (short formats):
        logical root → physical root table → ZC sequence (Nzc=139)
        cyclic shift per nCs config → time-domain preamble

ULCOMP packs everything into DfeIf_SlotConfigRequestIcm.txSlotConfig
DFE applies common phase precomp, IFFT, CP add, DAC.
```

**Threading**: 6 threads (`trd_sync`, `trd_l1c`, `trd_l1c_rx`, `trd_pdcch`, `trd_pdsch`, `trd_ulcomp`), each ICM-driven, slot-cadenced.

### Differences gNB vs UE

| Aspect | gNB (refc) | UE (nr_ue_phy) |
|---|---|---|
| Threading | Synchronous, slot-by-slot | 6 threads, ICM-driven |
| DCI | **Authored**: scheduler decides CCE+aggregation | **Searched blindly**: try every candidate |
| SSB | **Broadcasts** every 20 ms | **Searches** for it (cell search FSM) |
| Channel est | DMRS + SRS, makima+Wiener | DMRS only, freq-avg + time-avg flat copy |
| Equalizer | LMMSE / MRC / SISO | ZF / MMSE / MMSE-IRC |
| HARQ | Per-UE HARQ buffers | Per-process buffer, 16 processes |
| Precoding | Per PRG codebook | N/A (UE just demodulates) |
| Multi-user | Multiplexes many UEs per slot | Single UE (its own RNTI) |
| Power | Per-PUE link adaptation feedback loop | TPC-driven, no scheduling |

### Where we deviate from 3GPP

A senior engineer should be honest about this. The deliberate deviations:

1. **CHEST time interpolation** is flat-copy after time-averaging the DMRS symbols, not Wiener filtering. Spec doesn't mandate Wiener, but it's the textbook implementation.
2. **DCI blind search candidate count** — we cap at the spec-allowed maximum but don't implement all USS aggregation levels in CSS contexts (we keep CSS to {4,8,16}). That's actually spec-compliant for most CORESET configurations but you have to read TS 38.213 §10 carefully.
3. **PUSCH DFT-s-OFDM** — we implemented per-symbol DFT but pi/2-BPSK shaping is approximate (Q13 rather than full pi/4 spectral shaping).
4. **PRACH formats** — only short formats. Long formats (0–3) aren't implemented, which limits us to FR1 cells with appropriate config.
5. **Scrambling sequence init** — `(RNTI<<15) + scramblingId` is correct per TS 38.211 7.3.2.4 for PDSCH, but for some DCI formats we use the same generator with a different seed; verify against TS 38.211 Table 7.3.2.4-1 in any spec audit.
6. **Phase tracking RS (PT-RS)** — supported in framework but interpolation across symbols is simplified vs. the optimal MMSE-based algorithm.

Items 1, 4, 6 are explicit roadmap items if mobility/FR2 performance becomes critical.
