import sys
import os
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QVBoxLayout,
    QWidget,
    QPushButton,
    QLabel,
    QProgressBar,
    QTextEdit,
    QFileDialog,
)
from PyQt5.QtCore import Qt


class FileProcessorGUI(QMainWindow):
    def __init__(self):
        super().__init__()

        # Main window setup
        self.setWindowTitle("File Processor")
        self.setGeometry(100, 100, 600, 400)

        # Central widget
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        # Layout
        self.layout = QVBoxLayout()
        self.central_widget.setLayout(self.layout)

        # Folder selection button
        self.select_folder_btn = QPushButton("Select Root Folder")
        self.select_folder_btn.clicked.connect(self.select_folder)
        self.layout.addWidget(self.select_folder_btn)

        # Selected folder label
        self.folder_label = QLabel("No folder selected")
        self.folder_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.folder_label)

        # Start processing button
        self.start_btn = QPushButton("Start Processing")
        self.start_btn.setEnabled(False)
        self.start_btn.clicked.connect(self.start_processing)
        self.layout.addWidget(self.start_btn)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        self.layout.addWidget(self.progress_bar)

        # Log area
        self.log_area = QTextEdit()
        self.log_area.setReadOnly(True)
        self.layout.addWidget(self.log_area)

        # Selected folder path
        self.selected_folder = None

    def select_folder(self):
        """Open a folder selection dialog and set the selected folder."""
        folder = QFileDialog.getExistingDirectory(self, "Select Root Folder", os.getcwd())
        if folder:
            self.selected_folder = folder
            self.folder_label.setText(f"Selected Folder: {folder}")
            self.start_btn.setEnabled(True)
        else:
            self.folder_label.setText("No folder selected")
            self.start_btn.setEnabled(False)

    def start_processing(self):
        """Start processing files in the selected folder."""
        if not self.selected_folder:
            self.log_message("No folder selected. Please select a folder first.")
            return

        self.log_message(f"Starting processing for folder: {self.selected_folder}")
        # Simulate file processing
        self.process_files(self.selected_folder)

    def process_files(self, folder):
        """Simulate file processing with a progress bar."""
        # Get the list of files in the folder
        files = [f for f in os.listdir(folder) if os.path.isfile(os.path.join(folder, f))]
        total_files = len(files)

        if total_files == 0:
            self.log_message("No files found in the selected folder.")
            return

        self.progress_bar.setMaximum(total_files)
        for i, file in enumerate(files):
            # Simulate processing each file
            self.log_message(f"Processing file: {file}")
            self.progress_bar.setValue(i + 1)
            QApplication.processEvents()  # Keep UI responsive

        self.log_message("Processing complete!")

    def log_message(self, message):
        """Log a message to the log area."""
        self.log_area.append(message)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FileProcessorGUI()
    window.show()
    sys.exit(app.exec_())
