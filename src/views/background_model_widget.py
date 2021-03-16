import math

import matplotlib
import numpy as np
from PyQt5.QtWidgets import QHBoxLayout, QPushButton, QWidget, QVBoxLayout, QLabel, QCheckBox, QGridLayout
from PyQt5.QtCore import Qt

from models.background_method import BackgroundCorrection
from models.data_key import DataKey
from models.mathbot import interpolate_to_exponential
from models.settings import BACKGROUND1, BACKGROUND2
from models.spot import Spot

matplotlib.use('QT5Agg')
import matplotlib.pyplot as plt

from utils import ui_utils


class BackgroundModelWidget(QWidget):
    def __init__(self, results_dialog):
        QWidget.__init__(self)

        self.results_dialog = results_dialog

        layout = QVBoxLayout()
        title = QLabel("Background model")
        widget = self._create_graph_widget()
        layout.addWidget(title)
        layout.addWidget(widget)

        self.setLayout(layout)

        self.results_dialog.sample_tree.tree.currentItemChanged.connect(lambda i, j: self.replot_graph())
        self.results_dialog.configuration_changed.connect(self.replot_graph)
        # self.results_dialog.mass_peak_selection_changed.connect(self.update_mass_peaks_displayed)

    def _create_graph_widget(self):
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
        current_spot = self.results_dialog.sample_tree.current_spot()
        config = self.results_dialog.configuration_widget.current_config
        if config and current_spot:
            self.plot_background_graph(current_spot, config)
            # self.update_mass_peaks_displayed()

    def plot_background_graph(self, current_spot: Spot, config):
        axis = self.axes
        axis.clear()

        axis.spines['top'].set_visible(False)
        axis.spines['right'].set_visible(False)
        th_x = []
        th_y = []


        background_1 = current_spot.massPeaks[BACKGROUND1]
        background_2 = current_spot.massPeaks[BACKGROUND2]
        Th_peak = current_spot.massPeaks["ThO246"]

        x1 = np.mean([row.massAMUValue for row in background_1.rows])
        y1 = background_1.rows[0].data[config][DataKey.OUTLIER_RES_MEAN_STDEV]
        x2 = np.mean([row.massAMUValue for row in background_2.rows])
        y2 = background_2.rows[0].data[config][DataKey.OUTLIER_RES_MEAN_STDEV]
        for row in Th_peak.rows:
            th_x.append(row.massAMUValue)
            th_y.append(row.data[config][DataKey.OUTLIER_RES_MEAN_STDEV][0])

        x = np.arange(x1, x2, (x2-x1/100))
        if config.background_method == BackgroundCorrection.EXP:

            a, b, y_estimated_background, y_estimated_background_uncertainty = interpolate_to_exponential(
                point1=(0, y1[0]),
                error1=y1[1],
                point2=(x2 - x1, y2[0]),
                error2=y2[1],
                x=(x2 - x1) / 2
            )
            y = a * math.exp(b * x)
        elif config.background_method == BackgroundCorrection.LIN:
            m = (y2[0] - y1[0])/(x2 - x1)
            print(m)
            c = y1 - m * x1
            y = m * x + c
        else:
            for i in x:
                y = y2

        axis.plot(x, y, color='r')
        axis.plot(th_x, th_y, color='b')
        axis.set_xlabel("AMU")
        axis.set_ylabel("SBM normalised counts" if config.normalise_by_sbm else "Counts per second")
        plt.tight_layout()
        self.canvas.draw()
