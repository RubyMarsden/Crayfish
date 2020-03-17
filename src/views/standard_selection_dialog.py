from PyQt5.QtWidgets import QDialog, QCheckBox, QVBoxLayout, QDialogButtonBox, QGridLayout, QLabel


class StandardSelectionDialog(QDialog):
    def __init__(self, samples):
        QDialog.__init__(self)

        self.samples = samples

        self.setWindowTitle("Standard selection")
        self.setMinimumWidth(350)

        layout = QVBoxLayout()

        explanation_text = QLabel("Select which samples are standards:")

        self.standard_selection_checkboxes = {}
        checkbox_layout = QGridLayout()

        for i, sample in enumerate(samples):
            box = QCheckBox(sample.name)
            box.setChecked(False)

            checkbox_layout.addWidget(box, i//3, i % 3)
            self.standard_selection_checkboxes[sample] = box

        self.buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        layout.addWidget(explanation_text)
        layout.addLayout(checkbox_layout)
        layout.addWidget(self.buttonBox)

        self.setLayout(layout)

    def accept(self):
        for sample in self.samples:
            sample.is_standard = self.standard_selection_checkboxes[sample].isChecked()
        super().accept()
