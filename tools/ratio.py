import sys
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
from read import read_csi


def plot_ratio(csi_matrix):
    shape = csi_matrix.shape

    no_frames, no_subcarriers, no_rx, no_tx = shape
    pairs = [(rx, tx) for rx in range(no_rx) for tx in range(no_tx)]
    no_pairs = len(pairs)

    fig, ax = plt.subplots()
    fig.suptitle("CSI Amplitude Ratio Grid")
    fig.set_label("CSI Ratio")

    # Grid of ratio blocks: row pair / column pair.
    combined = np.full(
        (no_pairs * no_subcarriers, no_pairs * no_frames), np.nan, dtype=float
    )

    for r_idx, (rx_r, tx_r) in enumerate(pairs):
        first = csi_matrix[:, :, rx_r, tx_r].T  # shape: subcarriers x frames
        y0 = r_idx * no_subcarriers
        for c_idx, (rx_c, tx_c) in enumerate(pairs):
            second = csi_matrix[:, :, rx_c, tx_c].T
            x0 = c_idx * no_frames
            combined[y0 : y0 + no_subcarriers, x0 : x0 + no_frames] = first / second

            # Label center of the block with row/col pair names.
            ax.text(
                x0 + no_frames / 2,
                y0 + no_subcarriers / 2,
                f"(R{rx_r}T{tx_r})/(R{rx_c}T{tx_c})",
                color="white",
                ha="center",
                va="center",
                fontsize=8,
                weight="bold",
            )

    im = ax.imshow(combined, aspect="auto")

    # Divider lines between ratio blocks.
    for p in range(1, no_pairs):
        ax.axvline(p * no_frames, color="white", linewidth=1, linestyle="--")
        ax.axhline(p * no_subcarriers, color="white", linewidth=1, linestyle="--")

    ax.set_xlabel("Frame Index")
    ax.set_ylabel("Subcarrier Index")

    ax.xaxis.set_major_formatter(FuncFormatter(lambda v, pos: int(v % no_frames)))
    ax.yaxis.set_major_formatter(FuncFormatter(lambda v, pos: int(v % no_subcarriers)))

    plt.colorbar(im, ax=ax, label="Amplitude Ratio")
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    plot_ratio(read_csi(sys.argv[1]))
