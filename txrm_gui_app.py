# -*- coding: utf-8 -*-
"""
TXRM Parameters GUI Application
A standalone PySide6 GUI application for extracting Tomography scan metadata
from Xradia TXRM files and generating parameter CSV files.

Author: Generated from TXRMParams module
Date: 2026-02-11
"""

import sys
import os
from pathlib import Path
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QLineEdit, QSpinBox, QTextEdit, QFileDialog,
    QGridLayout, QGroupBox, QMessageBox
)
from PySide6.QtCore import Qt, QThread, Signal
import TXRMParams as tp


class ProcessWorker(QThread):
    """Worker thread for processing TXRM files without blocking the GUI"""
    finished = Signal()
    error = Signal(str)
    output = Signal(str)
    
    def __init__(self, input_file, output_file, start_sample, alignment_time, processing_time):
        super().__init__()
        self.input_file = input_file
        self.output_file = output_file
        self.start_sample = start_sample
        self.alignment_time = alignment_time
        self.processing_time = processing_time
    
    def run(self):
        """Execute the TXRM file processing"""
        try:
            # Validate input file
            if not self.input_file or not os.path.isfile(self.input_file):
                self.error.emit("Error: Input file does not exist!")
                return
            
            if not self.input_file.endswith('.txrm'):
                self.error.emit("Error: File must be a .txrm file!")
                return
            
            # Validate output file path
            if not self.output_file:
                self.error.emit("Error: Output file path not specified!")
                return
            
            self.output.emit(f"Opening file: {self.input_file}")
            
            # Generate the table using TXRMParams
            # For now, we'll use a single sample number (start_sample)
            # If you need a range, modify this to use range(self.start_sample, self.start_sample + count)
            table = tp.MakeTable(self.input_file, [self.start_sample], 
                                self.alignment_time, self.processing_time)
            
            if table is None:
                self.error.emit("Error: Failed to extract parameters from TXRM file!")
                return
            
            # Write the table to file
            try:
                with open(self.output_file, 'w') as f:
                    f.write(table)
                self.output.emit(f"Successfully wrote table to {self.output_file}")
                self.finished.emit()
            except IOError as e:
                self.error.emit(f"Error writing to file: {e}")
        
        except Exception as e:
            self.error.emit(f"Unexpected error: {str(e)}")


class TXRMParamsGUI(QMainWindow):
    """Main GUI window for TXRM Parameters application"""
    
    def __init__(self):
        super().__init__()
        self.input_file = ""
        self.output_file = ""
        self.worker = None
        self.init_ui()
    
    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("TXRM Parameters Extractor")
        self.setGeometry(100, 100, 900, 800)
        
        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # ===== File Selection Group =====
        file_group = QGroupBox("File Selection")
        file_layout = QGridLayout()
        
        # Input TXRM File
        input_label = QLabel("Input TXRM File:")
        self.input_text = QLineEdit()
        self.input_text.setReadOnly(True)
        self.input_button = QPushButton("Browse...")
        self.input_button.clicked.connect(self.select_input_file)
        
        file_layout.addWidget(input_label, 0, 0)
        file_layout.addWidget(self.input_text, 0, 1)
        file_layout.addWidget(self.input_button, 0, 2)
        
        # Output CSV File
        output_label = QLabel("Output CSV File:")
        self.output_text = QLineEdit()
        self.output_button = QPushButton("Change...")
        self.output_button.clicked.connect(self.select_output_file)
        
        file_layout.addWidget(output_label, 1, 0)
        file_layout.addWidget(self.output_text, 1, 1)
        file_layout.addWidget(self.output_button, 1, 2)
        
        file_group.setLayout(file_layout)
        main_layout.addWidget(file_group)
        
        # ===== Parameters Group =====
        params_group = QGroupBox("Processing Parameters")
        params_layout = QGridLayout()
        
        # Starting Sample Number
        sample_label = QLabel("Starting Sample Number:")
        self.sample_spinbox = QSpinBox()
        self.sample_spinbox.setMinimum(0)
        self.sample_spinbox.setMaximum(100000)
        self.sample_spinbox.setValue(1000)
        
        params_layout.addWidget(sample_label, 0, 0)
        params_layout.addWidget(self.sample_spinbox, 0, 1)
        
        # Alignment Time
        alignment_label = QLabel("Alignment Time (seconds):")
        self.alignment_spinbox = QSpinBox()
        self.alignment_spinbox.setMinimum(0)
        self.alignment_spinbox.setMaximum(100000)
        self.alignment_spinbox.setValue(15)
        
        params_layout.addWidget(alignment_label, 1, 0)
        params_layout.addWidget(self.alignment_spinbox, 1, 1)
        
        # Processing Time
        processing_label = QLabel("Processing Time (seconds):")
        self.processing_spinbox = QSpinBox()
        self.processing_spinbox.setMinimum(0)
        self.processing_spinbox.setMaximum(100000)
        self.processing_spinbox.setValue(15)
        
        params_layout.addWidget(processing_label, 2, 0)
        params_layout.addWidget(self.processing_spinbox, 2, 1)
        
        params_group.setLayout(params_layout)
        main_layout.addWidget(params_group)
        
        # ===== Output/Logging Group =====
        output_group = QGroupBox("Output Messages")
        output_layout = QVBoxLayout()
        
        self.output_text_edit = QTextEdit()
        self.output_text_edit.setReadOnly(True)
        self.output_text_edit.setMinimumHeight(300)
        
        output_layout.addWidget(self.output_text_edit)
        output_group.setLayout(output_layout)
        main_layout.addWidget(output_group)
        
        # ===== Action Buttons =====
        button_layout = QHBoxLayout()
        
        self.process_button = QPushButton("Create Output File")
        self.process_button.clicked.connect(self.process_file)
        self.process_button.setMinimumHeight(40)
        
        self.clear_button = QPushButton("Clear Messages")
        self.clear_button.clicked.connect(self.clear_messages)
        self.clear_button.setMinimumHeight(40)
        
        button_layout.addWidget(self.process_button)
        button_layout.addWidget(self.clear_button)
        main_layout.addLayout(button_layout)
        
        # Set final layout
        central_widget.setLayout(main_layout)
    
    def select_input_file(self):
        """Open file dialog to select input TXRM file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select TXRM File",
            "",
            "TXRM Files (*.txrm);;All Files (*)"
        )
        
        if file_path:
            self.input_file = file_path
            self.input_text.setText(file_path)
            
            # Auto-generate output filename
            self.generate_output_filename()
            self.log_message(f"Selected input file: {file_path}")
    
    def generate_output_filename(self):
        """Generate output filename from input filename"""
        if self.input_file:
            # Using Path.with_suffix() as in the notebook
            output_filename = str(Path(self.input_file).with_suffix("")) + "_Params.csv"
            self.output_file = output_filename
            self.output_text.setText(output_filename)
            self.log_message(f"Output filename generated: {output_filename}")
    
    def select_output_file(self):
        """Open file dialog to select/change output CSV file"""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save CSV File As",
            self.output_file,
            "CSV Files (*.csv);;All Files (*)"
        )
        
        if file_path:
            self.output_file = file_path
            self.output_text.setText(file_path)
            self.log_message(f"Output file changed to: {file_path}")
    
    def process_file(self):
        """Process the TXRM file and create the output CSV"""
        # Validate inputs
        if not self.input_file:
            self.log_message("ERROR: Please select an input TXRM file!")
            QMessageBox.warning(self, "Validation Error", "Please select an input TXRM file!")
            return
        
        if not self.output_file:
            self.log_message("ERROR: Please specify an output file!")
            QMessageBox.warning(self, "Validation Error", "Please specify an output file!")
            return
        
        # Disable buttons during processing
        self.process_button.setEnabled(False)
        
        # Create and start worker thread
        self.worker = ProcessWorker(
            self.input_file,
            self.output_file,
            self.sample_spinbox.value(),
            self.alignment_spinbox.value(),
            self.processing_spinbox.value()
        )
        
        self.worker.output.connect(self.log_message)
        self.worker.error.connect(self.log_error)
        self.worker.finished.connect(self.on_processing_finished)
        
        self.log_message("=" * 60)
        self.log_message("Starting file processing...")
        self.log_message(f"Input: {self.input_file}")
        self.log_message(f"Output: {self.output_file}")
        self.log_message(f"Start Sample: {self.sample_spinbox.value()}")
        self.log_message(f"Alignment Time: {self.alignment_spinbox.value()}s")
        self.log_message(f"Processing Time: {self.processing_spinbox.value()}s")
        self.log_message("=" * 60)
        
        self.worker.start()
    
    def on_processing_finished(self):
        """Called when processing is finished"""
        self.process_button.setEnabled(True)
        self.log_message("=" * 60)
        self.log_message("Processing completed successfully!")
        self.log_message("=" * 60)
        QMessageBox.information(self, "Success", "File processing completed successfully!")
    
    def log_message(self, message):
        """Add a message to the output text area"""
        self.output_text_edit.append(message)
        # Auto-scroll to bottom
        scrollbar = self.output_text_edit.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
    
    def log_error(self, error_message):
        """Add an error message to the output text area"""
        self.output_text_edit.append(f"ERROR: {error_message}")
        # Auto-scroll to bottom
        scrollbar = self.output_text_edit.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
        self.process_button.setEnabled(True)
        QMessageBox.critical(self, "Processing Error", error_message)
    
    def clear_messages(self):
        """Clear all messages from the output text area"""
        self.output_text_edit.clear()


def main():
    """Main entry point for the application"""
    app = QApplication(sys.argv)
    window = TXRMParamsGUI()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
