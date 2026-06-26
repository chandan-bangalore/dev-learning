# NR UE PHY Cell Search And Measurements

This note summarizes how cell search and SS/PBCH measurements are done in
`src/dl/sync`. It is intentionally written as a prototype and explanation,
not as a full code copy.

Main files:

- `src/dl/sync/dl_sync_controller.c`
- `src/dl/sync/dl_sync_pss_detection.c`
- `src/dl/sync/dl_sync_sss_detection.c`
- `src/dl/sync/dl_sync_ss_measurement.c`
- `src/dl/sync/dl_sync_pbch_baseband.c`
- `src/dl/sync/dl_sync_pbch.c`
- `src/dl/sync/dl_sync_cfo_estimation.c`
- `src/dl/sync/dl_sync_pbch_decoder.c`

## Big Picture

The UE receives time-domain IQ samples from the DFE. Cell search does:

```text
time-domain IQ
-> PSS correlation
-> NID2, rough SSB timing, coarse CFO hypothesis
-> CP-based fine CFO
-> SSS FFT/correlation
-> NID1, physical cell ID
-> SS measurements: RSRP, RSSI, RSRQ, SNR
-> PBCH baseband extraction
-> SSB index from PBCH DMRS
-> frame start index estimate
-> optional PBCH/MIB decode
```

The important cell identity formula is:

```text
physical_cell_id = 3 * NID1 + NID2
```

PSS gives `NID2`, which is only `0, 1, 2`.
SSS gives `NID1`, which is `0..335`.

## Controller Flow

The top-level cell search entry is:

```c
uint16_t dl_sync_controller_cell_search(
    ctrl,
    input_iq,
    input_len,
    aif_running_counter,
    arfcn,
    rf_gain_db,
    preferred_cell_id,
    l_max,
    is_long_data,
    dc_index);
```

Prototype:

```c
result = pss_detect(input_iq);
valid_candidates = remove_duplicate_pss_peaks(result);

for each candidate:
    sss_symbol_ptr = input_iq + timing_offset_from_pss_peak(candidate.peak_pos);
    sss = sss_detect(sss_symbol_ptr, candidate.nid2, candidate.cfo);

    if sss valid:
        cell_id = 3 * sss.nid1 + candidate.nid2;
        measure RSRP/RSSI/RSRQ/SNR;
        save candidate;

for each saved candidate:
    extract 4 SSB OFDM symbols around the PSS peak;
    find SSB index using PBCH DMRS correlation;
    estimate frame_start_index;
```

The controller stores results in `dl_sync_controller_result_t`, including:

```text
nid2
peak_pos
normalized_cfo
cell_id
rsrp
rsrq
rssi
snr
ssb_index
frame_start_index
pbch crc / mib payload after PBCH decode
```

## Step 1: PSS Detection

PSS detection is in `dl_sync_pss_detection.c`.

The code prepares references for all three possible `NID2` values:

```text
NID2 = 0
NID2 = 1
NID2 = 2
```

It also prepares several coarse CFO hypotheses. Depending on config, it may
search one, three, or five CFO hypotheses:

```text
0 only
-0.5, 0, +0.5
-1, -0.5, 0, +0.5, +1
```

These are normalized CFO values, roughly in units of subcarrier spacing.

Prototype:

```c
for nid2 in possible_nid2_values:
    pss_ref = generate_pss(nid2);

    for cfo_hypothesis in configured_cfo_hypotheses:
        corr_power = correlate(input_iq, pss_ref_with_cfo_hypothesis);
        peak = max(corr_power);

        if peak is strong:
            save_candidate(nid2, peak_pos, peak_value, coarse_cfo);
```

What we get from PSS:

```text
NID2              small part of cell ID
peak_pos          rough SSB/PSS timing position
peak_value        correlation strength
coarse CFO        from the best CFO hypothesis
```

## Step 2: Fine CFO From CP

After PSS, the code estimates finer CFO using cyclic prefix correlation in
`dl_sync_cp_cfo_est()`.

Idea:

```text
OFDM symbol = CP + useful_symbol

The CP is a copy of the end of the useful symbol.
If frequency offset exists, CP and the end of the symbol have a phase rotation.
That phase rotation gives CFO.
```

Prototype:

```c
complex_sum = 0;

for a few OFDM symbols around the PSS peak:
    cp_samples   = symbol_start[0 : cp_len - 1];
    tail_samples = symbol_start[fft_size : fft_size + cp_len - 1];
    complex_sum += sum(cp_samples * conj(tail_samples));

angle = atan2(imag(complex_sum), real(complex_sum));
fine_cfo_normalized = -angle / (2 * pi);
```

The controller combines coarse CFO and fine CFO:

```c
normalized_cfo = combine(coarse_cfo, fine_cfo);
```

This value is later used to compensate the SSS/PBCH samples.

## Step 3: SSS Detection

SSS detection is in `dl_sync_sss_detection.c`.

Input to SSS detection:

```text
time-domain samples around the SSS OFDM symbol
NID2 from PSS
normalized CFO from PSS + CP
```

First, the code applies fractional CFO correction:

```c
utils_correct_frac_cfo(input, time_buffer, norm_cfo, 0, fft_size);
```

Then it runs FFT:

```c
fftc_execute_fft(time_buffer, freq_buffer);
```

Then it extracts the middle 127 SSS subcarriers:

```c
rx_sss_seq = &freq_buffer[(fft_size - 128) / 2];
```

### How NID1 Is Found

< *"SSS is generated at the gNB using two fixed sequences, x0 and x1. x0 is shifted by m0, and x1 is shifted by m1. Since NID2 is already known from PSS, m0 has only 3 possible shifts, corresponding to floor(NID1/112) = 0, 1, 2. For each of those 3 x0 shift groups, the receiver multiplies the received SSS by that shifted x0 to remove it. Then it uses FHT to check all possible m1 values efficiently. Finally, it finds the strongest correlation peak. The peak tells us both the group and the m1 index, so we recover NID1, then calculate cell_id = 3*NID1 + NID2."*

NR SSS is generated from two length-127 sequences:

```text
SSS(n) = x0(n + m0) * x1(n + m1)
```

where:

```text
m0 = (15 * floor(NID1 / 112) + 5 * NID2) mod 127
m1 = NID1 mod 112
```

Because `floor(NID1 / 112)` can only be `0, 1, 2`, the code splits the search
into three groups for `m0`, and then uses a Fast Hadamard Transform to search
the `m1` candidates efficiently.

Prototype:

```c
sign_vector[0] = shifted_x0_for_group_0_and_nid2;
sign_vector[1] = shifted_x0_for_group_1_and_nid2;
sign_vector[2] = shifted_x0_for_group_2_and_nid2;

wkt:
rx_sss ≈ shifted_x0 * shifted_x1
rx_sss * shifted_x0 ≈ shifted_x0 * shifted_x1 * shifted_x0
Since shifted_x0 values are only +1 or -1: shifted_x0 * shifted_x0 = 1

for group in 0..2:
    temp = rx_sss_seq * sign_vector[group];
    temp = permute_ps(temp);
    temp = fast_hadamard_transform(temp);
    temp = permute_pl(temp);
    power[group] = abs2(temp);

index = argmax(power[0..3*128-1]);

nid1 = 112 * (index / 128) + (index % 128) - 1;
cell_id = 3 * nid1 + nid2;
```

So SSS gives:

```text
NID1
physical cell ID
```

Then the code generates the winning SSS reference and calls
`dl_sync_ss_measurement()` to calculate measurements.

## Step 4: SS Measurements

Measurements are done in `dl_sync_ss_measurement.c`.

Inputs:

```text
frequency-domain SSS symbol
reference SSS sequence for detected cell
rf_gain_db
dc_index
```

The code first computes frequency-domain power over 256 bins:

```c
utils_get_power(input, power_bins, 256);
```

Then it calculates three power sums:

```text
power_20RB = power over 20 RB SSB bandwidth
power_12RB = power over 12 RB center region
power_SSS  = power over 127 SSS REs
```

In the x86 path:

```c
for i = 8..247:
    power_20RB += power_bins[i];       // 240 REs = 20 RB

for i = 56..199:
    power_12RB += power_bins[i];       // 144 REs = 12 RB

for i = 64..190:
    power_SSS += power_bins[i];        // 127 SSS REs
```

### SSS Channel Response

The code extracts the 127 SSS REs:

```c
rx_sss_seq = &input[64];
```

Then it compensates by the reference SSS:

```c
sss_td[i] = rx_sss_seq[i] * ref_sss[i];
```

This is equivalent to:

```text
h_est = y * conj(x) / |x|^2
```

because SSS is real BPSK, `ref_sss[i]` is `+1` or `-1`, so:

```text
conj(ref_sss) = ref_sss
|ref_sss|^2 = 1
```

If the DC subcarrier is inside the SSS region, the code replaces it by an
average of neighbors.

### Signal And Noise Power

The compensated SSS channel estimate is transformed to time domain:

```c
ifft(sss_td) -> channel_impulse_response;
power = abs2(channel_impulse_response);
```

The strongest useful channel energy should be near tap `0`.

Noise is estimated away from the main tap:

```c
noise_power = average(power[18..107]);  // 90 bins
```

Signal power is estimated from tap 0 and nearby taps:

```c
sig_power = power[0];

for i = 1..3:
    sig_power += power[i] + power[fft_size - i];

sig_power = (sig_power - 7 * noise_power) / fft_size;
```

So conceptually:

```text
signal power = channel peak region - estimated noise
noise power  = average power away from the channel peak
```

### SNR

```c
snr_db = 10 * log10(sig_power / noise_power);
```

The code accepts the measurement if:

```text
SNR > -7 dB
```

### RSRP

```c
rsrp_dbm = 10 * log10(sig_power / 256) - rf_gain_db;
```

Notes:

- `sig_power` comes from the SSS-based channel impulse response.
- `/256` normalizes to the FFT/power scaling used by this implementation.
- `rf_gain_db` removes receiver gain so the result is closer to antenna-level
  received power.
- The code adds a temporary calibration offset:

```c
rf_gain_db += 12.0412;
```

### RSSI

The code estimates SS-RSSI from frequency-domain power:

```c
rssi =
    10 * log10(
        (
            power_20RB * 3 +
            (power_SSS / 127 * (127 + 17 * 2))
        ) / 4 / 256
    ) - rf_gain_db;
```

Meaning:

- SSB has 4 OFDM symbols.
- Symbol 0 is PSS over 20 RB.
- Symbols 1 and 3 are PBCH over 20 RB.
- Symbol 2 has SSS in the middle and PBCH around it.
- `power_20RB * 3` approximates three full 20-RB symbols.
- The SSS symbol has missing/non-uniform PBCH REs, so the code estimates it
  using `power_SSS / 127` scaled to the expected number of REs.
- `/4` averages over four SSB symbols.
- `/256` applies this implementation's FFT/power normalization.

### RSRQ

The usual relationship is:

```text
RSRQ = 10log10(N) + RSRP - RSSI_over_N_RB
```

The code uses 12 RB:

```c
rsrq =
    10.7918124605
    + rsrp
    - (10 * log10(power_12RB / 256) - rf_gain_db);
```

`10.7918124605` is:

```text
10 * log10(12)
```

So conceptually:

```text
RSRQ = 10log10(12 RB) + RSRP - RSSI measured over 12 RB
```

## Step 5: PBCH Baseband Extraction

After PSS/SSS, the controller extracts the 4 SSB OFDM symbols using
`dl_pbch_baseband_process()`.

Prototype:

```c
pbch_start_index = peak_pos + cp_len + 1;
pbch_start_index -= fft_size + cp_len;

cfo_to_comp = -normalized_cfo;

for ssb_symbol in 0..3:
    apply_cfo_correction(time_symbol);
    fft(time_symbol);
    copy middle 20 RBs into output buffer;
```

Output layout:

```text
symbol 0: PSS
symbol 1: PBCH
symbol 2: SSS + PBCH
symbol 3: PBCH
```

## Step 6: SSB Index From PBCH DMRS

The controller calls:

```c
dl_ssb_index_from_pbch(pbch_obj, &freq_data[nsc_per_sym], cell_id);
```

The code extracts PBCH DMRS and tries possible SSB indices:

```c
for i_ssb in 0..7:
    generate_pbch_dmrs(cell_id, i_ssb);
    corr = correlate(rx_dmrs, ref_dmrs);
    keep max corr;
```

The winning DMRS correlation gives the SSB index.

Current note from the code:

```text
If ssb_index is not zero, code logs it as false detection and forces 0.
```

That is project-specific behavior, not the generic NR rule.

## Step 7: Frame Timing

After the SSB index is known, the controller estimates frame start:

```c
frame_start_index =
    pss_peak_pos
    - ssb_index_dependent_offset
    - PSS_POS_3840KHz
    - filter_group_delay_correction;
```

This is the downlink timing result used to align the received frame.

Important distinction:

```text
This is not uplink Timing Advance from the gNB.
```

Uplink TA is commanded later by the gNB, for example in RAR or timing advance
MAC CE. In this sync code, the timing result is mainly:

```text
Where is the SSB?
Where is the radio frame boundary?
How much should local DL timing be adjusted?
```

## Step 8: PBCH / MIB Decode

MIB decode is done separately through:

```c
dl_sync_controller_mib_decoder(...)
```

It finds the matching cell from the latest cell-search result, extracts PBCH
baseband again, then calls:

```c
dl_pbch_process(...)
```

Prototype:

```c
freq_data = pbch_baseband_process(input_iq, timing, cfo);

apply_common_phase_correction(freq_data);
handle_dc_subcarrier(freq_data);

generate cached sequences:
    SSS reference
    PBCH DMRS reference
    PBCH scrambling sequence

extract SSS and PBCH DMRS;
LS channel estimate:
    h = rx_dmrs * conj(tx_dmrs)

estimate PBCH CFO if enabled:
    SSB-based CFO from PSS/SSS/DMRS phase
    DMRS-based CFO from PBCH DMRS + SSS phase

frequency-average channel estimates;
time-average channel estimates;
estimate PBCH SINR;

scale channel estimate for ZF/MMSE/MMSE-IRC;
equalize PBCH data;
QPSK demodulate to LLRs;
descramble;
polar rate recovery;
polar decode;
CRC24C check;

if CRC passes:
    descramble PBCH payload;
    deinterleave MIB bits;
    return mib_payload;
```

PBCH results saved in the cell result:

```text
crc_pass
mib_payload
pbch_sinr
pbch_evm
pbch_dmrs_cfo
ssb_cfo_est
```

## CFO Outputs

There are multiple CFO values in this sync path:

### PSS Coarse CFO

From the PSS correlation hypothesis:

```text
Which CFO-shifted PSS reference produced the best peak?
```

This gives a rough normalized CFO.

### CP Fine CFO

From cyclic-prefix phase:

```text
phase(CP vs repeated tail) -> fine normalized CFO
```

This is combined with the coarse PSS CFO as `normalized_cfo`.

### PBCH DMRS CFO

From PBCH DMRS and SSS phase relation:

```c
dl_pbch_dmrs_sss_cfo_est(dmrs_rx, sss_rx);
```

This returns CFO in Hz and is useful in tracking.

### SSB CFO

From PSS/SSS and PBCH DMRS phase relation:

```c
dl_ssb_cfo_est(...)
```

This also returns CFO in Hz and is useful after initial cell detection.

## Minimal End-To-End Prototype

```c
typedef struct {
    uint8_t nid2;
    uint16_t nid1;
    uint16_t cell_id;
    uint32_t pss_peak_pos;
    float normalized_cfo;
    float rsrp;
    float rssi;
    float rsrq;
    float snr;
    uint8_t ssb_index;
    int frame_start_index;
    uint8_t pbch_crc_pass;
    uint32_t mib_payload;
} CellSearchResult;

int cell_search(nr_cf32_t *iq, uint32_t iq_len, CellSearchResult *out)
{
    PssCandidate pss_list[MAX_CANDIDATES];
    int n_pss = pss_detect(iq, iq_len, pss_list);

    for (int c = 0; c < n_pss; c++) {
        PssCandidate *p = &pss_list[c];

        float fine_cfo = cp_cfo_est(iq, iq_len, p->peak_pos);
        float normalized_cfo = combine_cfo(p->coarse_cfo, fine_cfo);

        nr_cf32_t *sss_time = locate_sss_symbol(iq, p->peak_pos);

        SssResult sss;
        if (!sss_detect(sss_time, p->nid2, normalized_cfo, &sss))
            continue;

        out->nid2 = p->nid2;
        out->nid1 = sss.nid1;
        out->cell_id = 3 * sss.nid1 + p->nid2;
        out->pss_peak_pos = p->peak_pos;
        out->normalized_cfo = normalized_cfo;

        ss_measure(sss.freq_symbol, sss.ref_seq,
                   &out->rsrp, &out->rssi, &out->rsrq, &out->snr);

        nr_cf32_t *ssb_freq = pbch_baseband_extract(iq, p->peak_pos, normalized_cfo);
        out->ssb_index = detect_ssb_index_from_pbch_dmrs(ssb_freq, out->cell_id);
        out->frame_start_index = estimate_frame_start(p->peak_pos, out->ssb_index);

        return 1;
    }

    return 0;
}

int decode_mib(nr_cf32_t *iq, CellSearchResult *cell)
{
    nr_cf32_t *ssb_freq =
        pbch_baseband_extract(iq, cell->pss_peak_pos, cell->normalized_cfo);

    PbchResult pbch;
    cell->pbch_crc_pass = pbch_decode(ssb_freq, cell->cell_id,
                                      cell->ssb_index, &pbch);

    if (cell->pbch_crc_pass) {
        cell->mib_payload = pbch.mib_payload;
        return 1;
    }

    return 0;
}
```

## Interview Summary

If asked to explain this simply:

```text
PSS gives NID2, rough timing, and coarse CFO.
CP correlation refines CFO.
SSS uses NID2 and a fast Hadamard search to find NID1.
Cell ID is 3*NID1 + NID2.
SSS-based channel response gives RSRP and SNR.
Frequency-domain SSB power gives RSSI and RSRQ.
PBCH DMRS identifies SSB index and provides channel estimates for PBCH.
PBCH is equalized, demodulated, polar decoded, CRC checked, then MIB is extracted.
Frame start is derived from PSS peak position, SSB index, and filter delay correction.
```

