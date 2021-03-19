from typing import Callable

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QWidget, QCheckBox, QHBoxLayout, QButtonGroup, QRadioButton

from models.background_method import BackgroundCorrection
from models.configuration import Configuration
from models.spot import Spot


class ConfigurationWidget(QWidget):
    # signals get constructed before init method because they hack things
    state_changed = pyqtSignal()

    def __init__(self, sample_tree):
        super().__init__()

        self.current_config = None
        self.sample_tree = sample_tree

        self.sample_tree.tree.currentItemChanged.connect(self.on_selected_sample_change)
        
        self.exclude_spot_checkbox = QCheckBox("Exclude spot")
        self.exclude_spot_checkbox.stateChanged.connect(self.on_state_changed)
        self.exclude_spot_checkbox.stateChanged.connect(self.on_spot_exclusion)

        self.sbm_check_box = QCheckBox("Normalise to sbm")
        self.sbm_check_box.stateChanged.connect(self.on_state_changed)

        self.background_button_group = QButtonGroup()
        self.buttons = []

        for method in BackgroundCorrection:
            button = QRadioButton(method.value)
            button.method = method
            button.clicked.connect(self.on_state_changed)
            self.background_button_group.addButton(button)
            self.buttons.append(button)

        layout = QHBoxLayout()
        # The exclude spot widget is displayed elsewhere
        layout.addWidget(self.sbm_check_box)
        for button in self.buttons:
            layout.addWidget(button)

        self.setLayout(layout)

    def set_state(self, config: Configuration):
        self.blockSignals(True)
        for button in self.buttons:
            button.setChecked(button.method == config.background_method)
        self.sbm_check_box.setChecked(config.normalise_by_sbm)
        self.update_exclude_spot_checkbox(config)
        self.blockSignals(False)
        self.on_state_changed()

    def update_exclude_spot_checkbox(self, config=None):
        if config is None:
            config = self.current_config

        current_spot = self.sample_tree.current_spot()
        if current_spot is None:
            excluded = False
            enabled = False
        else:
            excluded = current_spot in config.excluded_spots
            enabled = True

        self.exclude_spot_checkbox.setEnabled(enabled)
        self.exclude_spot_checkbox.setChecked(excluded)

    def calculate_current_excluded_spots(self):
        config = self.current_config
        if config is None:
            return frozenset()

        previously_excluded_spots = config.excluded_spots
        current_spot = self.sample_tree.current_spot()
        if current_spot is None:
            return previously_excluded_spots

        is_excluded = self.exclude_spot_checkbox.isChecked()
        was_excluded = current_spot in previously_excluded_spots

        if is_excluded == was_excluded:
            return previously_excluded_spots

        excluded_spots = set(previously_excluded_spots)
        if is_excluded:
            excluded_spots.add(current_spot)
        else:
            excluded_spots.remove(current_spot)

        return frozenset(excluded_spots)

    ###########
    # Actions #
    ###########

    def on_selected_sample_change(self, current_tree_item, previous_tree_item):
        self.blockSignals(True)
        self.exclude_spot_checkbox.blockSignals(True)
        self.update_exclude_spot_checkbox()
        self.blockSignals(False)
        self.exclude_spot_checkbox.blockSignals(False)

    def on_state_changed(self):
        sbm_normalised = self.sbm_check_box.isChecked()
        background_method = self.background_button_group.checkedButton().method
        excluded_spots = self.calculate_current_excluded_spots()
        self.current_config = Configuration(
            sbm_normalised,
            background_method,
            excluded_spots
        )
        self.state_changed.emit()
        
    def on_spot_exclusion(self):
        is_flagged = self.exclude_spot_checkbox.isChecked()
        self.sample_tree.highlight_spot(is_flagged)

