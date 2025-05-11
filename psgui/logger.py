import io
import sys


class QTextEditLogger(io.TextIOBase):
    """Custom stream class that redirects output to QTextEdit"""

    def __init__(self, text_widget):
        super().__init__()
        self.text_widget = text_widget
        self.buffer = ""

    def write(self, text):
        # Buffer text until newline is encountered
        self.buffer += text
        if '\n' in self.buffer:
            lines = self.buffer.split('\n')
            self.buffer = lines[-1]  # Keep last line (might be incomplete)

            # Add complete lines to text box
            for i in range(len(lines)-1):
                self.text_widget.append(lines[i])

            # Scroll to bottom
            scrollbar = self.text_widget.verticalScrollBar()
            if scrollbar:
                scrollbar.setValue(scrollbar.maximum())

        return len(text)

    def flush(self):
        # Flush buffer if it contains content
        if self.buffer:
            self.text_widget.append(self.buffer)
            self.buffer = ""


def setup_logger(text_widget):
    """Set up log redirection, return original stdout"""
    logger = QTextEditLogger(text_widget)
    original_stdout = sys.stdout
    sys.stdout = logger
    return original_stdout
