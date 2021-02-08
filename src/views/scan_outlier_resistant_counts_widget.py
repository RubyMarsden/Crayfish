import matplotlib
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel

matplotlib.use('QT5Agg')
import matplotlib.pyplot as plt

from models.data_key import DataKey
from utils import ui_utils
from views.configuration_widget import ConfigurationWidget
from views.sample_tree import SampleTreeWidget


class ScanOutlierResistantCountsWidget(QWidget):
    def __init__(self, configs, samples):
        QWidget.__init__(self)

        self.samples = [sample for sample in samples if not sample.is_standard]

        self.setWindowTitle("Ages")
        self.setMinimumWidth(450)

        layout = QHBoxLayout()
        layout.addWidget(self._create_left_widget(self.samples, configs[0]))
        layout.addWidget(self._create_right_widget())
        self.setLayout(layout)

        self.sample_tree.set_samples(self.samples)

    def _create_right_widget(self):
        self.sample_tree = SampleTreeWidget()
        self.sample_tree.tree.currentItemChanged.connect(lambda i, j: self.replot_graph())

        layout = QVBoxLayout()
        layout.addWidget(self.sample_tree)

        widget = QWidget()
        widget.setLayout(layout)

        return widget

    def _create_left_widget(self, samples, current_config):
        self.configuration_widget = ConfigurationWidget(current_config)
        self.configuration_widget.configuration_state_changed.connect(self.replot_graph)

        # self.sample_flag_box = QCheckBox("Flag spot")
        # self.sample_flag_box.setChecked(False)
        # self.sample_flag_box.stateChanged.connect(self.on_flag_point_state_changed)

        top_bar = QHBoxLayout()
        top_bar.addWidget(QLabel("Sample and spot name"))
        top_bar.addWidget(self.configuration_widget, alignment=Qt.AlignCenter)
        # top_bar.addWidget(self.sample_flag_box, alignment=Qt.AlignRight)

        layout = QVBoxLayout()
        layout.addLayout(top_bar)
        layout.addWidget(self._create_age_graph_and_point_selection(samples))

        widget = QWidget()
        widget.setLayout(layout)
        return widget

    def _create_age_graph_and_point_selection(self, samples):

        graph_and_points = QWidget()
        layout = QVBoxLayout()

        fig = plt.figure()
        self.axes = plt.axes()

        graph_widget, self.canvas = ui_utils.create_figure_widget(fig, self)

        layout.addWidget(graph_widget)

        graph_and_points.setLayout(layout)

        return graph_and_points

    #############
    ## Actions ##
    #############

    def replot_graph(self):
        spot = self.sample_tree.tree.currentItem().spot
        config = self.configuration_widget.current_config
        self.plot_scan_cps_graph(spot, self.axes, config)

    def plot_scan_cps_graph(self, spot, axis, config):
        axis.clear()
        if spot is None:
            return
        axis.spines['top'].set_visible(False)
        axis.spines['right'].set_visible(False)
        for massPeak in spot.massPeaks.values():
            data_x = []
            data_y = []
            errors_y = []
            for i, row in enumerate(massPeak.rows):
                y, y_error = row.data[config][DataKey.OUTLIER_RES_MEAN_STDEV]
                data_x.append(i)
                data_y.append(y)
                errors_y.append(y_error)
            plt.errorbar(data_x, data_y, yerr=errors_y, linestyle="none", marker='o', label=massPeak.mpName)
            plt.legend(loc="upper left")

        axis.set_xlabel("Scan number")
        axis.set_ylabel("Counts per second")
        plt.tight_layout()
        self.canvas.draw()