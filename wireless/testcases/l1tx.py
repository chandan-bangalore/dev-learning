import numpy as np

def l1tx(
    inp_seq,
    nfft,
    sc_index_data,
    cp_len
):
    """
    OFDM modulation processing.

    Input:
        inp_seq        : Input binary sequence
        nfft           : FFT size
        sc_index_data  : Data subcarrier indices
        cp_len         : Cyclic prefix length

    Output:
        mod_out        : modulated IQ symbols 
        fd_data        : IQ samples mapped to RE's
        fd_data_shifted: fft shift before performing ifft
        ifft_out       : convert to time domain
        td_data        : Time-domain OFDM waveform with CP
    """

    # BPSK modulation
    mod_out = 2 * inp_seq - 1

    # Assign modulated symbols to subcarriers
    fd_data = np.zeros(nfft, dtype=complex)
    index = sc_index_data + (nfft // 2)
    fd_data[index] = mod_out
    
    # FFT shift
    fd_data_shifted = np.fft.fftshift(fd_data)

    # IFFT
    ifft_out = np.fft.ifft(fd_data_shifted, n=nfft)

    # Add cyclic prefix
    td_cp = np.concatenate(
        (ifft_out[-cp_len[1]:], ifft_out)
    )

    # Output time-domain data
    td_data = td_cp
    return mod_out, fd_data, fd_data_shifted, ifft_out, td_data