# import necessary libraries
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from l1tx import l1tx
from l1rx import l1rx
from plots import plot_tx_results

PLOT = False

# Configuration Parameters
nfft = 512     # 5MHz BW, 15KHz SCS = 25PRB x 12sc = 300sc
nsc_data = 240 # 12sc x 2rb x 10sym
nsc_dmrs = 24  # 6sc x 2rb x 2sym 
cp_len = np.array([44, 36])

def main():
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
        sc_index_data,
        cp_len
    )

    # Call L1 PHY RX processing chain
    rx_seq = l1rx(
        td_data,
        nfft,
        sc_index_data,
        cp_len
    )

    # Check the results
    if np.array_equal(inp_seq, rx_seq):
        print("TEST_PASSED")
    else:
        print("TEST_FAILED")

    # plot if required
    if PLOT:
        plot_tx_results(
            nfft,
            mod_out,
            fd_data,
            fd_data_shifted,
            ifft_out,
            td_data
        )    

# This is a Python convention — it means "only run main() if this file
# is executed directly, not when it's imported by another file."
if __name__ == "__main__":
    main()