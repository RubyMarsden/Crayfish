from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QWidget, QCheckBox, QHBoxLayout, QButtonGroup, QRadioButton

from models.background_method import BackgroundCorrection
from models.configuration import Configuration


class ConfigurationWidget(QWidget):
    # signals get constructed before init method because they hack things
    configuration_state_changed = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.current_config = None

        self.sbm_check_box = QCheckBox("Normalise to sbm")
        self.sbm_check_box.stateChanged.connect(self.on_state_changed)

        self.primary_background_filter_check_box = QCheckBox("Apply primary background filter")
        self.primary_background_filter_check_box.stateChanged.connect(self.on_state_changed)

        self.background_button_group = QButtonGroup()
        self.buttons = []

        for method in BackgroundCorrection:
            button = QRadioButton(method.value)
            button.method = method
            button.clicked.connect(self.on_state_changed)
            self.background_button_group.addButton(button)
            self.buttons.append(button)

        layout = QHBoxLayout()
        layout.addWidget(self.sbm_check_box)
        layout.addWidget(self.primary_background_filter_check_box)
        for button in self.buttons:
            layout.addWidget(button)

        self.setLayout(layout)

    def set_state(self, config: Configuration):
        self.blockSignals(True)
        self.current_config = config
        for button in self.buttons:
            button.setChecked(button.method == config.background_method)
        self.sbm_check_box.setChecked(config.normalise_by_sbm)
        self.primary_background_filter_check_box.setChecked(config.apply_primary_background_filter)
        self.blockSignals(False)
        self.on_state_changed()

    ###########
    # Actions #
    ###########

    def on_state_changed(self):
        sbm_normalised = self.sbm_check_box.isChecked()
        apply_primary_background_filter = self.primary_background_filter_check_box.isChecked()
        background_method = self.background_button_group.checkedButton().method
        self.current_config = Configuration(sbm_normalised, apply_primary_background_filter, background_method)
        self.configuration_state_changed.emit()


