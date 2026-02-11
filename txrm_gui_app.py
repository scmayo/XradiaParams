# Sample updated content here reflecting QLineEdit and SpinBox changes

from PyQt5.QtWidgets import QLineEdit, QSpinBox

class SampleApp(QWidget):
    def __init__(self):
        super().__init__()

        # Sample Number Input with QLineEdit
        self.sample_number_input = QLineEdit(self)
        self.sample_number_input.setValidator(QIntValidator())  # Ensure integer input

        # Alignment Time Input with QLineEdit
        self.alignment_time_input = QLineEdit(self)
        self.alignment_time_input.setValidator(QIntValidator())  # Ensure integer input

        # Processing Time Input with QLineEdit
        self.processing_time_input = QLineEdit(self)
        self.processing_time_input.setValidator(QIntValidator())  # Ensure integer input

        # Number of Samples SpinBox
        self.number_of_samples_input = QSpinBox(self)
        self.number_of_samples_input.setMinimum(1)  # Set minimum value
        self.number_of_samples_input.setMaximum(100)  # Set maximum value

        # Other UI components and layout
        # ...  

# Note: Adjust paths, import statements, and integrate this into your actual application structure accordingly.
