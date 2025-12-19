import sys
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
from read import read_csi


def plot_amplitude(csi_matrix):
    shape = csi_matrix.shape
    amplitude = np.abs(csi_matrix)

    no_frames, no_subcarriers, no_rx, no_tx = shape
    fig, ax = plt.subplots()
    fig.suptitle("CSI Amplitude Heatmap")
    fig.set_label("CSI Heatmap")

    combined = np.full((no_rx * no_subcarriers, no_tx * no_frames), np.nan, dtype=float)
    for rx in range(no_rx):
        for tx in range(no_tx):
            x0 = tx * no_frames
            y0 = rx * no_subcarriers
            combined[y0 : y0 + no_subcarriers, x0 : x0 + no_frames] = amplitude[
                :, :, rx, tx
            ].T
            ax.text(
                x0 + no_frames / 2,
                y0 + no_subcarriers / 2,
                f"RX{rx}-TX{tx}",
                color="white",
                ha="center",
                va="center",
                weight="bold",
            )

    im = ax.imshow(combined, aspect="auto")

    for tx in range(1, no_tx):
        ax.axvline(tx * no_frames, color="white", linewidth=1, linestyle="--")
    for rx in range(1, no_rx):
        ax.axhline(rx * no_subcarriers, color="white", linewidth=1, linestyle="--")

    ax.set_xlabel("Frame Index")
    ax.set_ylabel("Subcarrier Index")

    ax.xaxis.set_major_formatter(FuncFormatter(lambda v, pos: int(v % no_frames)))
    ax.yaxis.set_major_formatter(FuncFormatter(lambda v, pos: int(v % no_subcarriers)))

    plt.colorbar(im, ax=ax, label="Amplitude")
    plt.tight_layout()
    plt.savefig("amplitude.pdf")
    plt.show()


if __name__ == "__main__":
    plot_amplitude(read_csi(sys.argv[1]))
