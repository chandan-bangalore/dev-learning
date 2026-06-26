# Memtool Debug on ST050

End-to-end workflow for building/deploying PHY + macemu to **ST050**, running a
single CQI test vector under DDR, capturing memtool dumps, and parsing them on
the RPi to analyse a pass/fail.

Worked example throughout uses the CQI-6 test vector:

```
CQI_6_imcs8_coderate_0.59_5MHz_fs_30.72MHz_20RBs_SNR_3dB
```

---

## 1. Build and deploy PHY and macemu

Build the packages (see [How_to_build_and_run_phy.txt](How_to_build_and_run_phy.txt)
for the canonical recipe) and deploy to ST050.

```bash
cd build
rm -rf *
cmake .. -DCMAKE_TOOLCHAIN_FILE=../toolchains/startag-1.1.0.cmake -DNMM_RF_ACTIVE=On
make -j8 package

scp *.deb root@startag050.commagility.com:~/chandan/
```

> If you intend to analyse the per-`.bin` HARQ dump data, build with the
> `-DHARQ_DEBUG_DUMP_EN=TRUE` flag (see [Section 6](#6-harq-debug-dump-build)).

Log in to the target:

```bash
ssh root@startag050.commagility.com
```

---

## 2. Run the DDR test for one CQI test vector

Run the regression automation for the single CQI test vector. The CSV
(`tplan_test.csv`) should contain only the one row for the target TV.

```bash
./run_regression_automation.sh --csv tplan_test.csv
```

Example TV row:
`tv, rounds, repetition, test_pattern,ul/dl`
`${HOME}/workspace/startag_tv/CQI/CQI_6_imcs8_coderate_0.59_5MHz_fs_30.72MHz_20RBs_noisy_data/CQI_6_imcs8_coderate_0.59_5MHz_fs_30.72MHz_20RBs_SNR_3dB,1,1,0,0`

---

## 3. Preserve the upsample file across runs

`/tmp` is volatile and the regression run overwrites `/tmp/upsamp.txt` each time.
Keep a stable copy under `/home/root/chandan/` and restore it before every run.

```bash
# Save once (golden copy)
cp /tmp/upsamp.txt /home/root/chandan/upsamp.txt

# Restore before each run
cp /home/root/chandan/upsamp.txt /tmp/upsamp.txt
```

---

## 4. Enable memtool and restart PHY + macemu

### 4.1 Stop the running services

```bash
/opt/espace/uephy/oam/uephy_service.sh stop
# stop macemu (kill the running process)
```

### 4.2 Turn on memtool in phy_config.json

Edit the deployed config (`/opt/espace/uephy/phy/bin/phy_config.json`) and set
`memtoolEnable` to `true` in the `memtoolDump` block:

```json
"memtoolDump": {
    "memtoolEnable": true,
    "memtoolTimeDurationInSec": 500,
    "memtoolFreqInSec": 2,
    "memtoolMemoryValue": "0x3500ff33",
    "memtoolStopValue": "0x0f000000"
}
```

### 4.3 Start PHY

```bash
/opt/espace/uephy/oam/uephy_service.sh start
/opt/espace/uephy/oam/uephy_service.sh status   # confirm it is up
```

### 4.4 Run macemu with the `-e` flag

```bash
/opt/espace/uephy/macemu/bin/macemu \
    /tmp/CQI_6_imcs8_coderate_0.59_5MHz_fs_30.72MHz_20RBs_SNR_3dB/config.txt \
    -e -r 1 -t 2 -p 0
```

| Flag      | Meaning                          |
|-----------|----------------------------------|
| `-e`      | emulation / memtool capture mode |
| `-r 1`    | run count                        |
| `-t 2`    | test mode                        |
| `-p 0`    | port 0                           |

This produces the memtool `.bin` dumps under
`/tmp/uephy/memtool/`.

---

## 5. Copy memtool_parser to the RPi and build a config

### 5.1 scp memtool_parser to the RPi

```bash
scp build/testcases/submodules/memtool_parser/memtool_parser root@startag050.commagility.com:~/chandan
```

(See [How_to_parse_memtool.txt](How_to_parse_memtool.txt) for the full
memtool processing workflow.)

### 5.2 Create a config.txt from the memtool dump

Inspect the `.bin` filenames produced by the run and read off the `seqn`, `slot`
and the input-file indexes. Create a config file naming each index. Example:

```
root@startag050.commagility.com:~/chandan# cat cqi6_memtool/config_seqn6811.txt
seqn          = 6811
slot          = 1
dlConfigIndex = 77
configIndex   = 78
timeIndex     = 76
vspaFreqIndex = 79
```

Each index corresponds to the numeric prefix of the matching dump file
(e.g. `dbg_077_...`, `dbg_078_...`, `dbg_076_...`).

---

## 6. HARQ debug dump build

To analyse the per-`.bin` HARQ dump data, the parser (and PHY, if you want the
extra dumps) must be compiled with HARQ debug enabled:

```bash
cmake .. -DCMAKE_TOOLCHAIN_FILE=../toolchains/startag-1.1.0.cmake -DHARQ_DEBUG_DUMP_EN=TRUE
make -j8
```

---

## 7. Parse the dumps and analyse

Run the parser against the config you created:

```bash
./memtool_parser cqi6_memtool/config_seqn12842.txt
```

> Append `-f 0 -e 1 -D 1` to select time-domain input, equalizer and demodulator
> modes if you need to override the defaults. A parser built with
> `-DHARQ_DEBUG_DUMP_EN=TRUE` (Section 6) also writes the intermediate `*_llr.txt`
> dump files used in [Step 2](#72-step-2--analyse-the-harq-debug-dump-files).

A full run on ST050 looks like this:

```
root@startag050:~/chandan# ./memtool_parser cqi6_memtool/config_seqn12842.txt
Parsed args: useVspaFft=0, snr_estimation_rb_group_size=0
Processing cqi6_memtool/config_seqn12842.txt
Using seqn: 12842, slot: 2, dlConfigIndex: 121, configIndex: 122, timeIndex: 120, vspaFreqIndex: 123
[INFO] Opened cqi6_memtool/dbgv2_122_pdsch_CrcFail_seqn0000012842_slot2_configRequest.bin, file size = 76 bytes
[INFO] Versioned file detected (version = 0x30202)
[INFO] Detected ConfigRequest (v3.1+)
Test mode: PDSCH
CRC status: FAIL
[INFO] Loaded dbgv2_122_..._configRequest.bin successfully
[INFO] Loaded dbgv2_121_..._dlConfigRequest.bin successfully
[INFO] Loaded dbg_120_..._ci16.bin successfully
DCI[0]: PDCCH-SINR: 3.69dB, CCE_Index: 4, RNTI_Type: C-RNTI, RNTI_Value: 11151, DCI_Format: DCI_1_0, SearchSpaceType: UE_Specific, PayloadSize: 37, Payload: A3 80 80 00 00
DLSCH[0]: NumCodewords: 1, RBStart: 1, RBSize: 20, StartSymbolIndex: 2, NumSymbols: 12, SystemInformationIndicator: 0, BWPSize: 24, BWPStart: 42

logger register TRD_DL_PDSCH
... | dl_harq.c          |  36 | dlHarqCtx : 0xeb3d6bb0, hram_section_size: 115200, hram_total_size: 1843200
... | main.c             | 218 | GRANT_MODE = 0
... | dl_pdsch.c         | 459 | estCfo = 10, dc position = 69 rbStart = 1
... | dl_pdsch.c         | 514 | chanPower = 1537, noisePower = 656
... | dl_pdsch.c         | 517 | initial snrEst = 2.859391, final snrEst = 2
... | dl_pdsch.c         | 536 | data_length = 1920, dmrs_length = 480
... | dl_pdsch.c         | 594 | noisePowerScalar = 1251 (corrected=1)
... | dl_pdsch.c         | 603 | sfn: 380, slot: = 2, scr_cinit: 365395968
... | dl_pdsch_decoder.c | 102 | rnti value 11151, targetCodeRate 6020, tbSize 2280
... | dl_pdsch_decoder.c | 106 | number of codeblocks = 1, ldpc input length = 2400, ldpc output length = 12000
... | dl_pdsch_decoder.c | 108 | basegraph = 2, lifting size = 240, kdash = 2296
... | dl_pdsch_decoder.c | 120 | num_its = 10 mode = 0
... | dl_pdsch_decoder.c | 130 | rate matcher length[0] = 3840
... | dl_harq.c          | 218 | harq, harqProcessID: 0, ndi = 0, rv_idx: 0
... | dl_harq.c          | 237 | harq, slot_cur = 2, k: 2400, k_dash = 2296
... | dl_harq.c          | 249 | harq, very first tranmission, init RRC, set ndi to 1
... | dl_harq.c          | 314 | harq, no soft-combining, harq slot :2, harq buffer: 0x8ec29030
... | dl_pdsch_decoder.c | 227 | CRC16_FAIL
... | dl_pdsch.c         | 640 | set dataInd rnti 11151, tbSize 285, duplicateGrant: 0
```

The header lines confirm what the parser loaded — `CRC status: FAIL`, the decoded
`DCI[0]` (RNTI, DCI format, payload) and the `DLSCH[0]` allocation (RBStart,
RBSize, symbols, BWP). Check these against the TV first: a wrong RNTI, RB
allocation or DCI format here means the grant itself was mis-decoded and nothing
downstream can succeed.

### 7.1 Step 1 — read the `TRD_DL_PDSCH` trace first

**Always start here.** Walk the trace top to bottom and check **every** parameter
against the test-vector configuration — a single wrong value usually explains the
CRC fail and saves you from digging through dump files. Two failure families to
separate:

1. **Channel/RF quality** — the demod got a noisy signal (CFO, low SNR).
2. **Configuration mismatch** — the receive chain was set up differently from how
   the TV was generated (wrong MCS/coderate/TB size/LDPC params). These mean the
   decode was doomed regardless of SNR.

What each parameter means and when it is "wrong":

| Parameter (line) | Source | Healthy | Investigate when… |
|---|---|---|---|
| `estCfo` ([dl_pdsch.c:459](../../src/dl/pdsch/dl_pdsch.c#L459)) | `cn_cfoEstimation` | small (near 0) | large magnitude → residual carrier frequency offset; time-sync / DC-position / `rbStart` wrong. |
| `chanPower`, `noisePower` ([dl_pdsch.c:514](../../src/dl/pdsch/dl_pdsch.c#L514)) | chest power est. | `chanPower` ≫ `noisePower` | `noisePower` high relative to `chanPower` → poor channel; here 656 vs 1537 is a low ratio. **Both are fixed-point (float × 8192).** |
| `initial/final snrEst` ([dl_pdsch.c:517](../../src/dl/pdsch/dl_pdsch.c#L517)) | `cn_chest_sinr_bias_removal` | ≈ TV's configured SNR | far below the TV SNR (TV = `SNR_3dB`, trace shows `final snrEst = 2`) → confirms a low-SNR decode; if SNR looks fine but CRC still fails, suspect config mismatch instead. |
| `targetCodeRate`, `tbSize` ([dl_pdsch_decoder.c:102](../../src/dl/pdsch/dl_pdsch_decoder.c#L102)) | DCI/MCS | match TV's MCS/coderate (6020 ≈ 0.588 × 10240 ≈ 0.59) | mismatch with the TV → wrong DCI/MCS interpretation; the grant was decoded differently than generated. |
| `number of codeblocks`, `ldpc input/output length` ([dl_pdsch_decoder.c:106](../../src/dl/pdsch/dl_pdsch_decoder.c#L106)) | rate-match/segmentation | derived from TB size + BG | inconsistent with `tbSize`/`basegraph` → segmentation set up wrong. |
| `basegraph`, `lifting size`, `kdash` ([dl_pdsch_decoder.c:108](../../src/dl/pdsch/dl_pdsch_decoder.c#L108)) | LDPC params | match expected BG/Zc for the TB | wrong basegraph (BG1 vs BG2) or lifting size → LDPC decoder cannot converge. |
| `rate matcher length` ([dl_pdsch_decoder.c:130](../../src/dl/pdsch/dl_pdsch_decoder.c#L130)) | rate matching | matches allocated REs | mismatch → wrong G / rate matching. |
| `harqProcessID`, `ndi`, `rv_idx` ([dl_harq.c:218](../../src/dl/pdsch/dl_harq.c#L218)) | HARQ | match expected RV/process for the round | wrong `rv_idx` / unexpected soft-combining → HARQ buffer issue. |
| `CRC16_FAIL` / pass ([dl_pdsch_decoder.c:227](../../src/dl/pdsch/dl_pdsch_decoder.c#L227)) | TB CRC | pass | the verdict — fail means the TB did not decode. |

Rule of thumb: if `estCfo` is small and `snrEst` is in the ballpark of the TV's
configured SNR but CRC still fails, the cause is almost always a **configuration
mismatch** (the LDPC/rate-matching/MCS rows above) rather than channel quality.

### 7.2 Step 2 — analyse the HARQ debug dump files

Only when **Step 1 looks clean** (CFO small, `noisePower` reasonable vs
`chanPower`, and all LDPC/MCS parameters match the TV) move on to the per-stage
dump files. A parser built with `-DHARQ_DEBUG_DUMP_EN=TRUE` writes one `*_llr.txt`
file per receive-chain stage into the current directory:

```
root@startag050:~/chandan# ls *_llr.txt
pdsch_chest_dmrs_pos__slot0_llr.txt          harq_ldpc_eq_input_sym0..7__slot0_llr.txt
pdsch_chest_dmrs_sym0..3__slot0_llr.txt      harq_ldpc_demod_input__slot0_llr.txt
pdsch_chest_ls_sym0..3__slot0_llr.txt        harq_ldpc_demod_scale__slot0_llr.txt
pdsch_chest_h_est_sym0..3__slot0_llr.txt     harq_ldpc_demod_output__slot0_llr.txt
pdsch_chest_h_est_corr_sym0..3__slot0_llr.txt   harq_ldpc_descramble_input/output__slot0_llr.txt
pdsch_chest_h_est_avg__slot0_llr.txt         harq_ldpc_deinterleaver_d_slot0_llr.txt
harq_ldpc_eq_chest__slot0_llr.txt            harq_ldpc_rm_input/output_d_slot0_llr.txt
                                             harq_ldpc_decoder_input_d_slot0_llr.txt
                                             harq_ldpc_decoder_output_d / output_crc_d_slot0_llr.txt
                                             harq_input / harq_buffer_after / harq_output_slot2_llr.txt
```

Walk them **in receive-chain order** — the first stage that looks wrong is where
the fault is:

| Stage / file prefix | What it holds | Look for |
|---|---|---|
| `pdsch_chest_dmrs_pos`, `pdsch_chest_dmrs_symN` | DMRS positions and the extracted DMRS REs per symbol | DMRS landing on the wrong subcarriers → config mismatch. |
| `pdsch_chest_ls_symN` | least-squares channel estimate per DMRS symbol | wild/noisy LS estimate → bad input or DMRS sequence mismatch. |
| `pdsch_chest_h_est_symN` | per-symbol channel estimate (before CFO comp.) | discontinuities across subcarriers. |
| `pdsch_chest_h_est_corr_symN` | CFO-compensated channel estimate | residual rotation here → CFO not fully removed (cross-check `estCfo`). |
| `pdsch_chest_h_est_avg` | time-averaged channel estimate over DMRS symbols | should be smooth; noise here propagates to the equalizer. |
| `harq_ldpc_eq_chest`, `harq_ldpc_eq_input_symN` | equalizer reference and per-data-symbol equalizer input | constellation should be a recognisable QAM cloud; smeared/rotated → channel-est or CFO problem. |
| `harq_ldpc_demod_input`, `harq_ldpc_demod_scale`, `harq_ldpc_demod_output` | demodulator input (`eq_out`), scaling (`eq_scale`) and output LLRs | LLRs with no clear sign confidence → low effective SNR. |
| `harq_ldpc_descramble_*`, `harq_ldpc_deinterleaver_d` | descrambled / de-interleaved LLRs | wrong `scr_cinit` corrupts everything from here on. |
| `harq_ldpc_rm_input_d`, `harq_ldpc_rm_output_d` | de-rate-matched LLRs | length mismatch ties back to the `rate matcher length` trace line. |
| `harq_ldpc_decoder_input_d`, `harq_ldpc_decoder_output_d`, `harq_ldpc_decoder_output_crc_d` | LDPC decoder input LLRs and decoded output (pre/post CRC) | decoder not converging → upstream LLRs too noisy, or wrong basegraph/lifting size. |
| `harq_input`, `harq_buffer_after`, `harq_output` | HARQ buffer before/after this slot | unexpected soft-combining content on a first transmission. |

The dumps are the same data the x86 reference path produces, so a useful technique
is to run the identical TV through the x86 build and diff the per-stage dumps —
the first stage that diverges localises the bug.

---

## Quick reference — one cycle

```bash
# on ST050
cp /home/root/chandan/upsamp.txt /tmp/upsamp.txt          # restore golden upsamp
/opt/espace/uephy/oam/uephy_service.sh stop               # stop services
# edit phy_config.json -> memtoolDump.memtoolEnable = true
/opt/espace/uephy/oam/uephy_service.sh start
/opt/espace/uephy/oam/uephy_service.sh status
/opt/espace/uephy/macemu/bin/macemu \
    /tmp/CQI_6_imcs8_coderate_0.59_5MHz_fs_30.72MHz_20RBs_SNR_3dB/config.txt -e -r 1 -t 2 -p 0
# -> collect /opt/espace/uephy/phy/bin/*.bin, build config.txt, parse
./memtool_parser cqi6_memtool/config_seqn6811.txt -f 0 -e 1 -D 1
```
