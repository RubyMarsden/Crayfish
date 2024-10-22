import matplotlib
from PyQt5.QtWidgets import QHBoxLayout, QPushButton, QWidget, QVBoxLayout, QLabel, QCheckBox
from PyQt5.QtCore import Qt

from models.data_key import DataKey
import numpy as np

matplotlib.use('QT5Agg')
import matplotlib.pyplot as plt

from utils import ui_utils


class StandardLineWidget(QWidget):
    def __init__(self, results_dialog):
        QWidget.__init__(self)
        self.results_dialog = results_dialog

        self.samples = [sample for sample in self.results_dialog.samples if sample.is_standard]
        self.model_data = results_dialog.model_data

        layout = QHBoxLayout()
        layout.addLayout(self._create_widget())
        self.setLayout(layout)

        self.results_dialog.configuration_changed.connect(self.replot_graph)

    def _create_widget(self):
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Standard line"))
        layout.addWidget(self._create_standard_line_graph())

        return layout

    def _create_standard_line_graph(self):

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
        current_item = self.results_dialog.sample_tree.tree.currentItem()
        config = self.results_dialog.configuration_widget.current_config
        if config and current_item:
            self.plot_standard_line_graph(config)

    def plot_standard_line_graph(self, config):
        axis = self.axes
        axis.clear()

        axis.spines['top'].set_visible(False)
        axis.spines['right'].set_visible(False)
        xs = []
        x_errors = []
        ys = []
        y_errors = []
        for sample in self.samples:
            for spot in sample.spots:
                ratios = spot.data[config][DataKey.ACTIVITY_RATIOS]
                if len(ratios) == 0:
                    continue
                for ratio in ratios:
                    if isinstance(ratio, str):
                        continue
                    (x, dx), (y, dy) = ratio
                    xs.append(x)
                    x_errors.append(dx)
                    ys.append(y)
                    y_errors.append(dy)
        axis.errorbar(xs, ys, xerr=x_errors, yerr=y_errors, linestyle='none', marker='o')
        standard_line, standard_line_uncertainty = self.model_data[config][DataKey.STANDARD_LINE_GRADIENT]
        standard_line_MSWD = self.model_data[config][DataKey.STANDARD_LINE_MSWD]
        standard_x = np.arange(0.0, (max(xs)+max(x_errors)), max(xs)/4)
        standard_y = standard_line*standard_x
        axis.plot(standard_x, standard_y)
        string = f"Standard line gradient: {standard_line:.3f} Uncertainty: {standard_line_uncertainty:.3f} MSWD: {standard_line_MSWD:.3f} "
        axis.text(0.5, 1, string, transform=axis.transAxes, horizontalalignment="center")
        axis.set_xlabel("(238U)/(232Th)")
        axis.set_ylabel("(230Th)/(232Th)")
        self.canvas.draw()
