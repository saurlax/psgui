import sys
import numpy as np
from read import read_csi
from amplitude import plot_amplitude


def time_offset(csi, max_shift=20, pad_mode="zero"):
    """Shift frames along time axis with padding; positive = delay (shift right)."""
    frames, subc, rx, tx = csi.shape
    shift = np.random.randint(-max_shift, max_shift + 1)
    if shift == 0:
        return csi

    out = np.zeros_like(csi)
    if pad_mode == "edge":
        out[:] = csi[0]
    # copy overlapping region
    if shift > 0:
        out[shift:] = csi[: frames - shift]
    else:
        out[: frames + shift] = csi[-shift:]
    return out


def time_stretch(csi, stretch_min=0.9, stretch_max=1.1):
    """Resample along time axis with a random stretch; keeps frame length constant."""
    frames, subc, rx, tx = csi.shape
    factor = np.random.uniform(stretch_min, stretch_max)
    # new timeline maps current frame index -> source index
    src_idx = np.arange(frames) / factor
    src_idx = np.clip(src_idx, 0, frames - 1)

    real_part = np.empty_like(csi.real)
    imag_part = np.empty_like(csi.imag)
    flat_real = csi.real.reshape(frames, -1)
    flat_imag = csi.imag.reshape(frames, -1)

    for col in range(flat_real.shape[1]):
        real_part.reshape(frames, -1)[:, col] = np.interp(
            src_idx, np.arange(frames), flat_real[:, col]
        )
        imag_part.reshape(frames, -1)[:, col] = np.interp(
            src_idx, np.arange(frames), flat_imag[:, col]
        )

    return real_part + 1j * imag_part


def random_mask(csi, mask_ratio=0.15, contiguous=False):
    """Zero out random elements (or contiguous stripes if desired)."""
    frames, subc, rx, tx = csi.shape
    mask = np.zeros((frames, subc), dtype=bool)
    total = frames * subc
    k = int(total * mask_ratio)

    if contiguous and k > 0:
        span = max(1, int(mask_ratio * frames))
        start = np.random.randint(0, max(1, frames - span + 1))
        mask[start : start + span, :] = True
    else:
        idx = np.random.choice(total, size=k, replace=False)
        mask.flat[idx] = True

    masked = csi.copy()
    masked[mask, ...] = 0
    return masked


def amplitude_scale(csi, alpha_min=0.8, alpha_max=1.2):
    """Scale amplitudes by random factor; phase unchanged."""
    alpha = np.random.uniform(alpha_min, alpha_max)
    return csi * alpha


def freq_noise(csi, noise_scale=0.05):
    """Add complex Gaussian noise per subcarrier (frequency axis)."""
    amp = np.abs(csi)
    valid = amp[np.isfinite(amp)]
    amp_std = valid.std()
    sigma = noise_scale * amp_std
    noise = np.random.normal(0, sigma, size=csi.shape) + 1j * np.random.normal(
        0, sigma, size=csi.shape
    )
    return csi + noise


if __name__ == "__main__":
    csi = read_csi(sys.argv[1])
    csi = time_offset(csi)
    csi = time_stretch(csi)
    csi = random_mask(csi)
    csi = amplitude_scale(csi)
    csi = freq_noise(csi)

    plot_amplitude(csi)
