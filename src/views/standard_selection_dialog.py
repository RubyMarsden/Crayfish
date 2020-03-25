from PyQt5.QtWidgets import QDialog, QCheckBox, QVBoxLayout, QDialogButtonBox, QGridLayout, QLabel


class SampleSelectionDialog(QDialog):
    def __init__(self, samples, unavailable_samples):
        QDialog.__init__(self)

        self.samples = samples

        self.setWindowTitle(self.get_window_title())
        self.setMinimumWidth(350)

        layout = QVBoxLayout()

        explanation_text = QLabel(self.get_main_text())

        self.standard_selection_checkboxes = {}
        checkbox_layout = QGridLayout()

        for i, sample in enumerate(samples):
            box = QCheckBox(sample.name)
            box.setChecked(False)
            box.stateChanged.connect(self.check_selection_is_valid)
            box.setDisabled(sample in unavailable_samples)

            checkbox_layout.addWidget(box, i // 3, i % 3)
            self.standard_selection_checkboxes[sample] = box

        self.buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        self.check_selection_is_valid()

        layout.addWidget(explanation_text)
        layout.addLayout(checkbox_layout)
        layout.addWidget(self.buttonBox)

        self.setLayout(layout)

    def get_selected_samples(self):
        return [sample for sample in self.samples if self.standard_selection_checkboxes[sample].isChecked()]


class EquilibriumStandardSelectionDialog(SampleSelectionDialog):
    def __init__(self, samples, unavailable_samples):
        SampleSelectionDialog.__init__(self, samples, unavailable_samples)

    def get_window_title(self):
        return "Equiline standard selection"

    def get_main_text(self):
        return "Select which samples are in secular equilibrium:"

    def check_selection_is_valid(self):
        selected = [checkbox.isChecked() for checkbox in self.standard_selection_checkboxes.values()]
        valid = not all(selected) and any(selected)
        self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(valid)


class AgeStandardSelectionDialog(SampleSelectionDialog):
    def __init__(self, samples, unavailable_samples):
        SampleSelectionDialog.__init__(self, samples, unavailable_samples)

    def get_window_title(self):
        return "Age standard selection"

    def get_main_text(self):
        return "Select which sample is the age standard:"

    def check_selection_is_valid(self):
        selected = [checkbox.isChecked() for checkbox in self.standard_selection_checkboxes.values()]
        valid = sum(selected) == 1
        self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(valid)
