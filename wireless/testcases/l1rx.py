import numpy as np

def l1rx(
    td_data,
    nfft,
    nsc_data,
    sc_index_data,
    cp_len
):
    """
    OFDM demodulation processing.

    Input:
        td_data        : Time-domain OFDM waveform with CP
        nfft           : FFT size
        nsc_data       : Number of data subcarriers
        sc_index_data  : Data subcarrier indices
        cp_len         : Cyclic prefix configuration

    Output:
        rx_seq         : Recovered binary sequence
    """
    
    # Remove cyclic prefix
    td_data_no_cp = td_data[cp_len[1]:]

    # FFT
    fft_out = np.fft.fft(td_data_no_cp, n=nfft)

    # FFT shift
    fd_data_shifted = np.fft.fftshift(fft_out)

    # Extract data subcarriers
    index = sc_index_data % nfft
    demod_out = fd_data_shifted[index]

    # BPSK demodulation
    # +1 -> bit 1
    # -1 -> bit 0
    rx_seq = (np.real(demod_out) >= 0).astype(int)

    # Return RX results
    return rx_seq