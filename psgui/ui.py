import os
import sys
import json
import shutil
from PyQt6.QtWidgets import (QMainWindow, QTextEdit,
                             QPushButton, QVBoxLayout, QHBoxLayout, QWidget, QLabel,
                             QLineEdit, QGroupBox, QFormLayout, QApplication,
                             QSplitter)
from PyQt6.QtCore import pyqtSlot, Qt

from psgui.config import DEFAULT_CONFIG, load_config, save_config
from psgui.runner import ScriptRunner
from psgui.logger import setup_logger
from psgui.visualizer import CSIVisualizer


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.config = load_config()
        self.initUI()
        self.script_runner = None
        self.last_manifest_entry = None
        self.last_csi_file_path = None
        self.original_stdout = setup_logger(self.info_display)
        print("Log output redirected to UI")

    def closeEvent(self, event):
        """Save configuration and restore stdout when window is closed"""
        sys.stdout = self.original_stdout
        self.save_current_config()
        event.accept()

    def save_current_config(self):
        """Save current UI configuration"""
        try:
            self.config["duration"] = float(self.duration_input.text())
        except (ValueError, TypeError):
            self.config["duration"] = DEFAULT_CONFIG["duration"]

        self.config["picoscenes_rx_command"] = self.command_input.text()
        self.config["subfolder_name"] = self.subfolder_input.text()

        if not save_config(self.config):
            print("Error saving configuration")

    def initUI(self):
        # Set window properties
        self.setWindowTitle('CSI Collector')
        # Increased size for visualization
        self.setGeometry(100, 100, 1000, 800)

        central_widget = QWidget()
        main_layout = QVBoxLayout(central_widget)

        # Add settings group
        config_group = QGroupBox("Collection Settings")
        config_layout = QFormLayout()

        # Collection duration input
        self.duration_input = QLineEdit(
            str(self.config.get("duration", DEFAULT_CONFIG["duration"])))
        config_layout.addRow(
            "Collection Duration (seconds):", self.duration_input)

        # Command parameter input
        self.command_input = QLineEdit(self.config.get(
            "picoscenes_rx_command", DEFAULT_CONFIG["picoscenes_rx_command"]))
        config_layout.addRow("PicoScenes RX Command:", self.command_input)

        # Subfolder name input
        self.subfolder_input = QLineEdit(
            self.config.get("subfolder_name", "default"))
        config_layout.addRow("Subfolder Name:", self.subfolder_input)

        config_group.setLayout(config_layout)
        main_layout.addWidget(config_group)

        # Collection button
        buttons_layout = QHBoxLayout()
        self.run_button = QPushButton("Collect CSI")
        self.run_button.clicked.connect(self.on_run_button_clicked)
        buttons_layout.addWidget(self.run_button)
        main_layout.addLayout(buttons_layout)

        # Create splitter for upper and lower sections
        splitter = QSplitter(Qt.Orientation.Vertical)
        splitter.setChildrenCollapsible(False)
        main_layout.addWidget(splitter)

        # Upper section: labels and logs
        upper_widget = QWidget()
        h_layout = QHBoxLayout(upper_widget)

        # Left side: label input
        left_panel = QVBoxLayout()
        left_panel.addWidget(QLabel("Labels (one per line):"))
        self.labels_input = QTextEdit()
        self.labels_input.setPlaceholderText("activity=normal")
        left_panel.addWidget(self.labels_input)
        h_layout.addLayout(left_panel)

        # Right side: information display
        right_panel = QVBoxLayout()
        right_panel.addWidget(QLabel("Status & Logs:"))
        self.info_display = QTextEdit()
        self.info_display.setReadOnly(True)
        self.info_display.setPlaceholderText("Log output will appear here")
        right_panel.addWidget(self.info_display)
        h_layout.addLayout(right_panel)

        splitter.addWidget(upper_widget)

        # Lower section: visualization
        viz_widget = QWidget()
        viz_layout = QVBoxLayout(viz_widget)

        # Add CSI visualization component
        self.csi_viz = CSIVisualizer(viz_widget)
        viz_layout.addWidget(self.csi_viz)

        splitter.addWidget(viz_widget)

        # Set initial splitter sizes
        # Upper panel smaller, visualization larger
        splitter.setSizes([300, 400])

        self.setCentralWidget(central_widget)

    @pyqtSlot()
    def on_run_button_clicked(self):
        self.run_button.setEnabled(False)
        print("Running data collection script...")
        QApplication.processEvents()

        # Get current parameters
        command = self.command_input.text()
        try:
            duration = float(self.duration_input.text())
        except ValueError:
            print("Invalid duration value. Using default.")
            duration = DEFAULT_CONFIG["duration"]

        self.script_runner = ScriptRunner(command, duration)
        self.script_runner.signals.finished.connect(self.on_script_finished)
        self.script_runner.signals.error.connect(self.on_script_error)
        self.script_runner.start()

    @pyqtSlot()
    def on_script_finished(self):
        print("Processing CSI files...")
        QApplication.processEvents()
        self.process_csi_files()
        self.run_button.setEnabled(True)

    @pyqtSlot(str)
    def on_script_error(self, error_msg):
        """Script execution error callback"""
        print(f"Error running script: {error_msg}")
        self.run_button.setEnabled(True)

    def parse_labels(self):
        """Parse labels from text input"""
        labels = {}
        text = self.labels_input.toPlainText().strip()

        if not text:
            return labels

        for line in text.split('\n'):
            if '=' in line:
                key, value = line.split('=', 1)
                labels[key.strip()] = value.strip()

        return labels

    def process_csi_files(self):
        """Find, move CSI files and update manifest"""
        try:
            # Get subfolder name
            subfolder_name = self.subfolder_input.text().strip()
            if not subfolder_name:
                subfolder_name = "default"

            # Ensure target directory exists
            target_dir = os.path.join('data', subfolder_name)
            if not os.path.exists(target_dir):
                os.makedirs(target_dir)

            # Get all .csi files in current directory
            csi_files = [f for f in os.listdir('.') if f.endswith('.csi')]

            if not csi_files:
                print("No .csi files found.")
                self.csi_viz.clear_plot()
                return

            # Parse labels from input
            labels_dict = self.parse_labels()

            # Load existing manifest.json if it exists
            manifest_path = os.path.join(target_dir, 'manifest.json')
            manifest = []
            if os.path.exists(manifest_path):
                try:
                    with open(manifest_path, 'r') as f:
                        manifest = json.load(f)
                except json.JSONDecodeError:
                    print("Warning: manifest.json exists but is not valid. Creating a new one.")

            # Process each .csi file
            last_csi_file = None
            for csi_file in csi_files:
                # Save last file for visualization
                if last_csi_file is None:
                    last_csi_file = csi_file

                # Move file to target directory
                target_file_path = os.path.join(target_dir, csi_file)
                shutil.move(csi_file, target_file_path)

                # Add entry to manifest
                entry = {
                    "data": csi_file,
                    "labels": labels_dict
                }
                manifest.append(entry)
                self.last_manifest_entry = entry

            # Save updated manifest to subdirectory
            with open(manifest_path, 'w') as f:
                json.dump(manifest, f, indent=2)
            print(f"Updated manifest saved to {manifest_path}")

            # Print summary
            print(f"\nSuccess! Processed {len(csi_files)} CSI files.")
            if self.last_manifest_entry:
                print(json.dumps(self.last_manifest_entry, indent=2))

            # Visualize last CSI file
            if last_csi_file:
                self.last_csi_file_path = os.path.join(
                    target_dir, last_csi_file)
                self.csi_viz.plot_csi_heatmap(self.last_csi_file_path)
            else:
                self.csi_viz.clear_plot()

        except Exception as e:
            print(f"Error: {str(e)}")
            self.csi_viz.clear_plot()
