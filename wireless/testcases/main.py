# import necessary libraries
import numpy as np
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
from l1tx import l1tx

# Configuration Parameters
nfft = 512     # 5MHz BW, 15KHz SCS = 25PRB x 12sc = 300sc
nsc_data = 240 # 12sc x 2rb x 10sym
nsc_dmrs = 24  # 6sc x 2rb x 2sym 
cp_len = np.array([22, 18])

sc_index_min = -nsc_data // 2
sc_index_max = nsc_data // 2 + 1

sc_index_data = np.concatenate(
    (np.arange(sc_index_min, 0), np.arange(1, sc_index_max))
)

# Generate Input Sequence
inp_seq = np.random.randint(0, 2, nsc_data)

# Call L1 PHY TX processing chain
mod_out, fd_data, fd_data_shifted, ifft_out, td_data = l1tx(
    inp_seq,
    nfft,
    nsc_data,
    sc_index_data,
    cp_len
)

# Plot
plt.figure(figsize=(10, 12))
nrows = 6
ncols = 1
# 1. Input / BPSK
plt.subplot(nrows, ncols, 1)
plt.stem(
    np.arange(1, len(mod_out) + 1),
    np.abs(mod_out)
)
plt.xlim(1, len(mod_out))
plt.title("BPSK Modulation")
plt.ylabel("|Symbol|")
plt.grid(True)

# 2. Subcarrier mapping
plt.subplot(nrows, ncols, 2)
plt.stem(
    np.arange(1, nfft + 1),
    np.abs(fd_data)
)
plt.xlim(1, nfft)
plt.title("BPSK Symbols Assigned to Subcarriers")
plt.ylabel("|Symbol|")
plt.grid(True)

# 3. FFT shift
plt.subplot(nrows, ncols, 3)
plt.stem(
    np.arange(1, nfft + 1),
    np.abs(fd_data_shifted)
)
plt.xlim(1, nfft)
plt.title("After FFT Shift")
plt.ylabel("|Symbol|")
plt.grid(True)

# 4. Time-domain OFDM symbol
plt.subplot(nrows, ncols, 4)
plt.stem(
    np.arange(1, nfft + 1),
    np.abs(ifft_out)
)
plt.xlim(1, nfft)
plt.title("Time Domain OFDM Symbol")
plt.ylabel("|Amplitude|")
plt.grid(True)

# 5. OFDM + CP
plt.subplot(nrows, ncols, 5)
plt.stem(
    np.arange(1, len(td_data) + 1),
    np.abs(td_data)
)
plt.xlim(1, len(td_data))
plt.title("OFDM Symbol with Cyclic Prefix")
plt.ylabel("|Amplitude|")
plt.grid(True)

# 6. Final output
plt.subplot(nrows, ncols, 6)
plt.stem(
    np.arange(1, len(td_data) + 1),
    np.abs(td_data)
)
plt.xlim(1, len(td_data))
plt.title("td_data - Final Time Domain Sequence")
plt.xlabel("Sample")
plt.ylabel("|Amplitude|")
plt.grid(True)

plt.tight_layout()

plt.show()