from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog, QTabWidget, QVBoxLayout, QPushButton, QHBoxLayout, QCheckBox, QWidget

from views.configuration_widget import ConfigurationWidget
from views.sample_tree import SampleTreeWidget
from views.sbm_time_series_widget import SBMTimeSeriesWidget
from views.cps_time_series_widget import cpsTimeSeriesWidget
from views.scan_outlier_resistant_counts_widget import ScanOutlierResistantCountsWidget
from views.standard_line_widget import StandardLineWidget
from views.age_results_widget import AgeResultsWidget


class ResultsDialog(QDialog):
    def __init__(self, configs, samples):
        QDialog.__init__(self)
        # Right widget has to be created first as tabs depend on sample tree - so that must be instantiated first.
        right_widget = self._create_right_widget()
        left_widget = self._create_left_widget(configs, samples)

        layout = QHBoxLayout()
        layout.addLayout(left_widget)
        layout.addLayout(right_widget)
        self.setLayout(layout)

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
        layout.addWidget(self.continue_button,  alignment=Qt.AlignRight)

        return layout

    def _create_left_widget(self, configs, samples):
        self.configuration_widget = ConfigurationWidget(configs[0])

        self.tabs = QTabWidget()
        self.tabs.addTab(SBMTimeSeriesWidget(samples), "1. SBM time series")
        self.tabs.addTab(cpsTimeSeriesWidget(configs, samples), "2. Counts per second")
        self.tabs.addTab(ScanOutlierResistantCountsWidget(self), "3. Outlier resistant scan means")
        self.tabs.addTab(StandardLineWidget(configs, samples), "4. Standard line")
        self.tabs.addTab(AgeResultsWidget(configs, samples), "5. Ages")

        layout = QVBoxLayout()
        layout.addWidget(self.configuration_widget)
        layout.addWidget(self.tabs)

        return layout
