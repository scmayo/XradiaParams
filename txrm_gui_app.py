# Update the txrm_gui_app.py file to add 'Number of Samples' SpinBox

import sys
from PyQt5.QtWidgets import QApplication, QWidget, QSpinBox, QVBoxLayout

class ParametersGroup(QWidget):
    def __init__(self):
        super().__init__()

        # Existing SpinBox for Starting Sample Number
        self.starting_sample_number = QSpinBox(self)
        self.starting_sample_number.setMinimum(1)
        self.starting_sample_number.setValue(1)
        self.starting_sample_number.setSuffix(' Starting Sample Number')

        # New SpinBox for Number of Samples
        self.number_of_samples = QSpinBox(self)
        self.number_of_samples.setMinimum(1)
        self.number_of_samples.setMaximum(100000)
        self.number_of_samples.setValue(1)
        self.number_of_samples.setSuffix(' Number of Samples')

        # Layout to place the widgets
        layout = QVBoxLayout(self)
        layout.addWidget(self.starting_sample_number)
        layout.addWidget(self.number_of_samples)
        self.setLayout(layout)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = ParametersGroup()
    window.show()
    sys.exit(app.exec_())