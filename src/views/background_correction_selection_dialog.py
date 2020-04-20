from PyQt5.QtWidgets import QDialog, QCheckBox, QVBoxLayout, QDialogButtonBox, QGridLayout, QLabel, QButtonGroup


class BackgroundSelectionDialog(QDialog):
    def __init__(self):
        QDialog.__init__(self)

        self.setWindowTitle("Select background correction method")
        self.setMinimumWidth(350)

        layout = QVBoxLayout()

        explanation_text = QLabel()

        checkbox_group = QButtonGroup(self)
        checkbox_group.setExclusive(True)

        self.box1 = QCheckBox("Exponential")
        self.box1.setChecked(False)
        self.box1.stateChanged.connect(self.check_selection_is_valid)

        self.box2 = QCheckBox("Linear")
        self.box2.setChecked(False)
        self.box2.stateChanged.connect(self.check_selection_is_valid)

        self.box3 = QCheckBox("No further 230Th background correction")
        self.box3.setChecked(False)
        self.box3.stateChanged.connect(self.check_selection_is_valid)

        checkbox_group.addButton(self.box1)
        checkbox_group.addButton(self.box2)
        checkbox_group.addButton(self.box3)

        checkbox_layout = QGridLayout()
        checkbox_layout.addWidget(self.box1)
        checkbox_layout.addWidget(self.box2)
        checkbox_layout.addWidget(self.box3)

        self.buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        self.check_selection_is_valid()

        layout.addWidget(explanation_text)
        layout.addLayout(checkbox_layout)
        layout.addWidget(self.buttonBox)

        self.setLayout(layout)

    def check_selection_is_valid(self):
        selected = [checkbox.isChecked() for checkbox in [self.box1, self.box2, self.box3]]
        valid = any(selected)
        self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(valid)

    def get_background_correction(self):
        for checkbox in [self.box1, self.box2, self.box3]:
            if checkbox.isChecked():
                return checkbox.text()
        return None
