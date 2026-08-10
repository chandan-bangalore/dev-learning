import numpy as np
import matplotlib
import matplotlib.pyplot as plt

def plot_tx_results(
    nfft,
    mod_out,
    fd_data,
    fd_data_shifted,
    ifft_out,
    td_data
):
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