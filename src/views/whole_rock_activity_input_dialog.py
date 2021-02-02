from PyQt5.QtWidgets import QDialog, QVBoxLayout, QDialogButtonBox, QGridLayout, QLabel, QDoubleSpinBox


class WholeRockActivityDialog(QDialog):
    def __init__(self, samples):
        QDialog.__init__(self)

        self.setWindowTitle("Input whole rock activity ratios for non-standard samples")
        self.setMinimumWidth(450)

        layout = QVBoxLayout()

        explanation_text = QLabel("Whole rock value inputs assuming that the activity ratio of the starting melt from "
                                  "which the zircons grew is equal to this value.")

        sample_list = [sample for sample in samples if not sample.is_standard]

        sample_input_form = QGridLayout()
        title_name = QLabel("Sample name")
        title_wr = QLabel("Whole rock activity value")
        title_uncertainty = QLabel("Whole rock activity value 2σ")

        sample_input_form.addWidget(title_name, 0, 1)
        sample_input_form.addWidget(title_wr, 0, 2)
        sample_input_form.addWidget(title_uncertainty, 0, 3)

        for i, sample in enumerate(sample_list):
            name = QLabel(sample.name)

            wr_input = QDoubleSpinBox()
            wr_input.setDecimals(3)
            wr_input.setSingleStep(0.001)
            wr_input.valueChanged.connect(self.on_wr_value_changed(sample))

            uncertainty_input = QDoubleSpinBox()
            uncertainty_input.setDecimals(3)
            uncertainty_input.setSingleStep(0.001)
            uncertainty_input.valueChanged.connect(self.make_get_value_from_uncertainty_spin_box(sample))

            sample_input_form.addWidget(name, i+1, 1)
            sample_input_form.addWidget(wr_input, i+1, 2)
            sample_input_form.addWidget(uncertainty_input, i+1, 3)

        self.buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        layout.addWidget(explanation_text)
        layout.addLayout(sample_input_form)
        layout.addWidget(self.buttonBox)
        self.setLayout(layout)

    def on_wr_value_changed(self, sample):
        def get_value_from_wr_spin_box(d):
            sample.WR_activity_ratio = d
        return get_value_from_wr_spin_box

    def make_get_value_from_uncertainty_spin_box(self, sample):
        def get_value_from_uncertainty_spin_box(d):
            sample.WR_activity_ratio_uncertainty = d
        return get_value_from_uncertainty_spin_box
