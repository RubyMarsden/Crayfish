from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QWidget, QCheckBox, QHBoxLayout, QButtonGroup, QRadioButton

from models.background_method import BackgroundCorrection
from models.configuration import Configuration


class ConfigurationWidget(QWidget):
    # signals get constructed before init method because they hack things
    configuration_state_changed = pyqtSignal()

    def __init__(self, default_config: Configuration):
        super().__init__()
        self.current_config = default_config

        self.sbm_check_box = QCheckBox("Normalise to sbm")
        self.sbm_check_box.setChecked(default_config.normalise_by_sbm)
        self.sbm_check_box.stateChanged.connect(self.on_state_changed)

        self.background_button_group = QButtonGroup()
        buttons = []

        for method in BackgroundCorrection:
            button = QRadioButton(method.value)
            button.setChecked(method == default_config.background_method)
            button.method = method
            button.clicked.connect(self.on_state_changed)
            self.background_button_group.addButton(button)
            buttons.append(button)

        layout = QHBoxLayout()
        layout.addWidget(self.sbm_check_box)
        for button in buttons:
            layout.addWidget(button)

        self.setLayout(layout)

    ###########
    # Actions #
    ###########

    def on_state_changed(self):
        sbm_normalised = self.sbm_check_box.isChecked()
        background_method = self.background_button_group.checkedButton().method
        self.current_config = Configuration(sbm_normalised, background_method)
        self.configuration_state_changed.emit()


