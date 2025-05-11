import subprocess
import time
from threading import Thread
from PyQt6.QtCore import pyqtSignal, QObject


class ScriptRunnerSignals(QObject):
    finished = pyqtSignal()
    error = pyqtSignal(str)


class ScriptRunner(Thread):
    def __init__(self, option, duration):
        super().__init__()
        self.option = option
        self.duration = duration
        self.process = None
        self.signals = ScriptRunnerSignals()

    def run(self):
        try:
            self.process = subprocess.Popen(['PicoScenes', self.option],
                                            stdout=subprocess.PIPE,
                                            stderr=subprocess.PIPE)

            time.sleep(self.duration)
            if self.process.poll() is None:
                self.process.kill()
                self.process.wait()
            self.signals.finished.emit()
        except Exception as e:
            self.signals.error.emit(str(e))
