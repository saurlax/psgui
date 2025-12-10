import sys
from CSIKit.reader import get_reader
from CSIKit.util import csitools


def read_csi(path):
    reader = get_reader(path)
    csidata = reader.read_file(path, scaled=True)
    csi_matrix = csitools.get_CSI(csidata, metric="complex")[0]
    shape = csi_matrix.shape
    print(f"CSI with (frames, subcarriers, rx, tx): {shape}")

    return csi_matrix


if __name__ == "__main__":
    print(read_csi(sys.argv[1]))
