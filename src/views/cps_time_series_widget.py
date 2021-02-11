import matplotlib
from PyQt5.QtWidgets import QHBoxLayout, QPushButton, QWidget, QVBoxLayout, QLabel, QCheckBox, QGridLayout
from PyQt5.QtCore import Qt

from models.data_key import DataKey

matplotlib.use('QT5Agg')
import matplotlib.pyplot as plt

from views.sample_tree import SampleTreeWidget
from utils import ui_utils


class cpsTimeSeriesWidget(QWidget):
    def __init__(self, results_dialog):
        QWidget.__init__(self)

        self.results_dialog = results_dialog

        layout = QHBoxLayout()
        layout.addLayout(self._create_left_widget())
        self.setLayout(layout)

        self.results_dialog.sample_tree.tree.currentItemChanged.connect(lambda i, j: self.replot_graph())
        self.results_dialog.configuration_widget.configuration_state_changed.connect(self.replot_graph)

    def _create_left_widget(self):
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Sample and spot name"))
        layout.addWidget(self._create_cps_graph_and_point_selection())

        return layout


    def _create_cps_graph_and_point_selection(self):

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
            self.plot_cps_graph(current_item.spot.massPeaks, config)

    def plot_cps_graph(self, mass_peaks, config):
        axis = self.axes
        axis.clear()
        axis.spines['top'].set_visible(False)
        axis.spines['right'].set_visible(False)
        for massPeak in mass_peaks.values():
            data_x = []
            data_y = []
            x = 0
            for row in massPeak.rows:
                number_of_scans = len(row.data[config][DataKey.CPS])
                xs = [i + x for i in range(number_of_scans)]
                ys = [value for value in row.data[config][DataKey.CPS]]
                x += number_of_scans
                data_x.extend(xs)
                data_y.extend(ys)
            axis.plot(data_x, data_y, label=massPeak.mpName)
            axis.legend(loc="upper left")
        axis.set_xlabel("Spot number")
        axis.set_ylabel("SBM normalised counts" if config.normalise_by_sbm else "Counts per second")
        plt.tight_layout()
        self.canvas.draw()



    def make_background_graph(self):
        pass
