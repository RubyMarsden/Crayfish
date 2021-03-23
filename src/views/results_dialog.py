from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import QDialog, QTabWidget, QVBoxLayout, QPushButton, QHBoxLayout, QCheckBox, QWidget, QGridLayout

from models.configuration import Configuration
from views.configuration_widget import ConfigurationWidget
from views.sample_tree import SampleTreeWidget
from views.sbm_time_series_widget import SBMTimeSeriesWidget
from views.cps_time_series_widget import cpsTimeSeriesWidget
from views.scan_outlier_resistant_counts_widget import ScanOutlierResistantCountsWidget
from views.standard_line_widget import StandardLineWidget
from views.age_results_widget import AgeResultsWidget


class ResultsDialog(QDialog):
    configuration_changed = pyqtSignal()
    mass_peak_selection_changed = pyqtSignal()
    spots_flagged_changed = pyqtSignal()

    def __init__(self, samples, default_config, ensure_config_calculated_callback, model_data, export_data_callback):
        QDialog.__init__(self)
        self.samples = samples
        self.ensure_config_calculated_callback = ensure_config_calculated_callback
        self.model_data = model_data
        self.export_data_callback = export_data_callback
        self.mass_peaks_selected = []
        self.mass_peak_check_boxes = []

        # Sample tree widget has to be created first as configuration widget depends on it. Widgets within the
        # configuration widget are in both the right and left layouts.
        self.sample_tree = SampleTreeWidget()
        self.configuration_widget = ConfigurationWidget(self.sample_tree)

        right_layout = self._create_right_layout()
        left_layout = self._create_left_layout(samples)

        layout = QHBoxLayout()
        layout.addLayout(left_layout)
        layout.addLayout(right_layout)
        self.setLayout(layout)

        self.configuration_widget.state_changed.connect(self.on_configuration_widget_state_changed)

        self.configuration_widget.set_state(default_config)
        self.sample_tree.set_samples(samples)

    def _create_right_layout(self):
        self.export_button = QPushButton("Export")
        self.export_button.clicked.connect(self.on_export_button_pushed)

        layout = QVBoxLayout()
        layout.addWidget(self.configuration_widget.exclude_spot_checkbox)
        layout.addWidget(self.sample_tree)
        layout.addWidget(self.export_button, alignment=Qt.AlignRight)

        return layout

    def _create_left_layout(self, samples):
        self.tabs = QTabWidget()
        self.tabs.addTab(SBMTimeSeriesWidget(self), "1. SBM time series")
        self.tabs.addTab(cpsTimeSeriesWidget(self), "2. Counts per second")
        self.tabs.addTab(ScanOutlierResistantCountsWidget(self), "3. Outlier resistant scan means")
        self.tabs.addTab(StandardLineWidget(self), "5. Standard line")
        self.tabs.addTab(AgeResultsWidget(self), "6. Ages")

        self.mass_checkboxes = self.make_mass_check_boxes(samples)

        layout = QVBoxLayout()
        layout.addWidget(self.tabs)
        layout.addWidget(self.configuration_widget)
        layout.addLayout(self.mass_checkboxes)

        return layout

    def make_mass_check_boxes(self, samples):
        sample = samples[0]
        masses = sample.spots[0].mpNames

        checkbox_layout = QGridLayout()

        for i, mass in enumerate(masses):
            box = QCheckBox(mass)
            box.mass_peak = mass
            box.setChecked(True)
            box.stateChanged.connect(self.on_mass_peak_selection_changed)
            checkbox_layout.addWidget(box, i // 3, i % 3)
            self.mass_peaks_selected.append(mass)
            self.mass_peak_check_boxes.append(box)
        return checkbox_layout

    ###########
    # Actions #
    ###########

    def on_configuration_widget_state_changed(self):
        self.ensure_config_calculated_callback(self.configuration_widget.current_config)
        self.configuration_changed.emit()

    def on_mass_peak_selection_changed(self):
        self.mass_peaks_selected.clear()
        for box in self.mass_peak_check_boxes:
            if box.isChecked():
                self.mass_peaks_selected.append(box.mass_peak)

        self.mass_peak_selection_changed.emit()

    def on_export_button_pushed(self):
        current_config = self.configuration_widget.current_config
        self.export_data_callback(current_config, self.samples, "output")

