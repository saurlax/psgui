from PyQt6.QtWidgets import QSizePolicy
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import os
import numpy as np
import matplotlib
from CSIKit.reader import PicoScenesBeamformReader
from CSIKit.util import csitools
matplotlib.use('Qt5Agg')  # Use Qt5Agg backend


class CSIVisualizer(FigureCanvas):
    """CSI data visualization class that embeds matplotlib heatmap in Qt interface"""

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = self.fig.add_subplot(111)

        FigureCanvas.__init__(self, self.fig)
        self.setParent(parent)

        # Set FigureCanvas size policy
        FigureCanvas.setSizePolicy(self,
                                   QSizePolicy.Policy.Expanding,
                                   QSizePolicy.Policy.Expanding)
        FigureCanvas.updateGeometry(self)

        # Initialize empty plot
        self.clear_plot()

    def clear_plot(self):
        """Clear plot and display default message"""
        self.axes.clear()
        self.axes.text(0.5, 0.5, "CSI Visualizer",
                       horizontalalignment='center',
                       verticalalignment='center',
                       transform=self.axes.transAxes)
        self.axes.set_axis_off()
        self.draw()

    def plot_csi_heatmap(self, csi_file_path):
        """Generate heatmap from CSI file using CSIKit"""
        try:
            if not os.path.exists(csi_file_path):
                print(f"CSI file not found: {csi_file_path}")
                self.clear_plot()
                return False

            # Load CSI data using CSIKit
            try:
                # Removed initial loading log
                
                # Initialize PicoScenes reader
                pico_reader = PicoScenesBeamformReader()

                # Read the CSI file
                csidata = pico_reader.read_file(csi_file_path, scaled=True)

                # Extract CSI matrix
                csi_matrix, no_frames, no_subcarriers = csitools.get_CSI(
                    csidata)

                print(f"Successfully loaded CSI data: {no_frames} frames, {no_subcarriers} subcarriers")

                # Get the magnitude of the complex CSI values
                csi_magnitude = np.abs(csi_matrix)
                
                print(f"Original CSI data shape: {csi_magnitude.shape}")
                
                # Directly extract the first rx-tx antenna pair (0,0)
                # We assume data is in shape (packets, subcarriers, rx, tx)
                csi_magnitude = csi_magnitude[:, :, 0, 0]
                
                # Removed antenna pair selection log
                
                # Simple bounds for visualization
                min_sc_idx = 0
                max_sc_idx = csi_magnitude.shape[1] - 1
                timestamps = None
                
            except Exception as e:
                print(f"Failed to parse CSI data with CSIKit: {str(e)}")
                # Fallback: generate random data for example
                no_frames = 100
                no_subcarriers = 64
                csi_magnitude = np.random.rand(no_frames, no_subcarriers)
                min_sc_idx = 0
                max_sc_idx = no_subcarriers-1
                timestamps = None

            # Plot heatmap
            self.axes.clear()
            im = self.axes.imshow(csi_magnitude.T,  # Transpose for correct orientation
                                 aspect='auto',
                                 origin='lower',
                                 cmap='viridis',
                                 interpolation='none',
                                 extent=[0, csi_magnitude.shape[0]-1, min_sc_idx, max_sc_idx])
            
            # Set axis labels with data from CSIKit
            self.axes.set_xlabel('Frame Index' if timestamps is None else 'Time (ms)')
            self.axes.set_ylabel('Subcarrier Index')
            self.axes.set_title(f'CSI Amplitude Heatmap (RX1-TX1)')
            
            # If timestamps are available, set custom x-ticks at regular intervals
            if timestamps is not None and len(timestamps) > 1:
                # Convert timestamps to milliseconds relative to first frame
                rel_timestamps_ms = [(ts - timestamps[0])/1000 for ts in timestamps]
                # Set 5 tick marks along the x-axis
                tick_indices = np.linspace(0, len(timestamps)-1, 5).astype(int)
                self.axes.set_xticks(tick_indices)
                self.axes.set_xticklabels([f"{rel_timestamps_ms[idx]:.1f}" for idx in tick_indices])

            # Add colorbar
            self.fig.colorbar(im, ax=self.axes, label='Amplitude')

            # Auto-adjust layout and draw
            self.fig.tight_layout()
            self.draw()
            return True

        except Exception as e:
            print(f"Visualization error: {str(e)}")
            self.clear_plot()
            return False
