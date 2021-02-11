from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import QDialog, QTabWidget, QVBoxLayout, QPushButton, QHBoxLayout, QCheckBox, QWidget, QGridLayout

from views.configuration_widget import ConfigurationWidget
from views.sample_tree import SampleTreeWidget
from views.sbm_time_series_widget import SBMTimeSeriesWidget
from views.cps_time_series_widget import cpsTimeSeriesWidget
from views.scan_outlier_resistant_counts_widget import ScanOutlierResistantCountsWidget
from views.standard_line_widget import StandardLineWidget
from views.age_results_widget import AgeResultsWidget


class ResultsDialog(QDialog):
    configuration_changed = pyqtSignal()

    def __init__(self, samples, default_config, ensure_config_calculated_callback):
        QDialog.__init__(self)
        self.samples = samples
        self.ensure_config_calculated_callback = ensure_config_calculated_callback

        # Right widget has to be created first as tabs depend on sample tree - so that must be instantiated first.
        right_widget = self._create_right_widget()
        left_widget = self._create_left_widget(samples)

        layout = QHBoxLayout()
        layout.addLayout(left_widget)
        layout.addLayout(right_widget)
        self.setLayout(layout)

        self.configuration_widget.configuration_state_changed.connect(self.on_configuration_widget_state_changed)

        self.configuration_widget.set_state(default_config)
        self.sample_tree.set_samples(samples)

    def _create_right_widget(self):
        self.continue_button = QPushButton("Continue")
        self.continue_button.clicked.connect(self.accept)

        self.sample_tree = SampleTreeWidget()

        self.sample_flag_box = QCheckBox("Flag spot")
        self.sample_flag_box.setChecked(False)

        # self.sample_flag_box.stateChanged.connect(self.on_flag_point_state_changed)
        layout = QVBoxLayout()
        layout.addWidget(self.sample_flag_box)
        layout.addWidget(self.sample_tree)
        layout.addWidget(self.continue_button, alignment=Qt.AlignRight)

        return layout

    def _create_left_widget(self, samples):
        self.configuration_widget = ConfigurationWidget()

        self.tabs = QTabWidget()
        self.tabs.addTab(SBMTimeSeriesWidget(self), "1. SBM time series")
        self.tabs.addTab(cpsTimeSeriesWidget(self), "2. Counts per second")
        self.tabs.addTab(ScanOutlierResistantCountsWidget(self), "3. Outlier resistant scan means")
        self.tabs.addTab(StandardLineWidget(self), "4. Standard line")
        self.tabs.addTab(AgeResultsWidget(self), "5. Ages")

        self.mass_checkboxes = self.make_mass_check_boxes(samples)

        layout = QVBoxLayout()
        layout.addWidget(self.tabs)
        layout.addWidget(self.configuration_widget)
        layout.addLayout(self.mass_checkboxes)

        return layout

    def make_mass_check_boxes(self, samples):

        for sample in samples:
            for spot in sample.spots:
                masses = spot.mpNames

        checkbox_layout = QGridLayout()

        for i, mass in enumerate(masses):
            box = QCheckBox(mass)
            checkbox_layout.addWidget(box, i // 3, i % 3)

        return checkbox_layout

    # TODO fix this:
    def on_selected_sample_change(self, current_tree_item, previous_tree_item):
        if current_tree_item is None:
            self.axis.clear()
            return

        if current_tree_item.is_sample:
            self.sample_flag_box.setVisible(False)
            return

        self.sample_flag_box.setVisible(True)
        self.sample_flag_box.setChecked(current_tree_item.spot.is_flagged)

    # TODO fix this:
    def on_flag_point_state_changed(self):
        sample = self.sample_tree.tree.currentItem()
        sample.spot.is_flagged = self.sample_flag_box.isChecked()

    def on_configuration_widget_state_changed(self):
        config = self.configuration_widget.current_config
        self.ensure_config_calculated_callback(config)

        self.configuration_changed.emit()
