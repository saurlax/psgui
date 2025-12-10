import sys
import numpy as np
import matplotlib.pyplot as plt
from read import read_csi


def plot_complex(csi_matrix):
    first = [0, 0]
    second = [1, 0]
    frames = (
        csi_matrix[:, 0, first[0], first[1]] / csi_matrix[:, 0, second[0], second[1]]
    )

    fig = plt.figure(figsize=(10, 4))
    plane = fig.add_subplot(1, 2, 1, projection="polar")
    amp_ax = fig.add_subplot(1, 2, 2)

    plane.scatter(np.angle(frames), np.abs(frames))
    plane.set_title(f"Complex Plane (R{first[0]}T{first[1]}/R{second[0]}T{second[1]})")
    r_max = np.max(np.abs(frames))
    plane.set_rmax(r_max)
    plane.grid(True, linestyle="--", alpha=0.4)
    phase_ax = amp_ax.twinx()

    amp_line = amp_ax.plot(np.abs(frames), label="Amplitude", color="tab:blue")
    phase_line = phase_ax.plot(np.angle(frames), label="Phase", color="tab:orange")

    amp_ax.set_xlabel("Frame Index")
    amp_ax.set_ylabel("Amplitude")
    phase_ax.set_ylabel("Phase (rad)")
    phase_ax.set_ylim(-np.pi, np.pi)

    amp_ax.set_title("Amplitude & Phase")
    lines = amp_line + phase_line
    labels = [l.get_label() for l in lines]
    amp_ax.legend(lines, labels, loc="upper right")
    amp_ax.grid(True, linestyle="--", alpha=0.4)

    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    plot_complex(read_csi(sys.argv[1]))
