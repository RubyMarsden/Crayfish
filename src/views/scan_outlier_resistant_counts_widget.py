import matplotlib
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel

matplotlib.use('QT5Agg')
import matplotlib.pyplot as plt

from models.data_key import DataKey
from utils import ui_utils

# TODO fix lines which are over the top of each other
class ScanOutlierResistantCountsWidget(QWidget):
    def __init__(self, results_dialog):
        QWidget.__init__(self)

        self.results_dialog = results_dialog

        self.errorbars = []

        self.setLayout(self._create_widget())

        results_dialog.sample_tree.tree.currentItemChanged.connect(lambda i, j: self.replot_graph())
        results_dialog.configuration_changed.connect(self.replot_graph)
        self.results_dialog.mass_peak_selection_changed.connect(self.update_mass_peaks_displayed)

    def _create_widget(self):

        layout = QVBoxLayout()
        layout.addWidget(QLabel("Sample and spot name"))
        layout.addWidget(self._create_age_graph_and_point_selection())

        return layout

    def _create_age_graph_and_point_selection(self):

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
            self.plot_scan_cps_graph(current_item.spot, config)

    def plot_scan_cps_graph(self, spot, config):
        axis = self.axes
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
            errorbars = axis.errorbar(data_x, data_y, yerr=errors_y, linestyle="none", marker='', label=massPeak.mpName)
            errorbars.max_y = max([y + e for y, e in zip(data_y, errors_y)])
            errorbars.min_y = min([y - e for y, e in zip(data_y, errors_y)])
            self.errorbars.append(errorbars)

        axis.legend(loc="upper left")
        axis.set_xlabel("Scan number")
        axis.set_ylabel("Counts per second")
        self.canvas.draw()

    def update_mass_peaks_displayed(self):
        min_y = float("inf")
        max_y = 0
        for errorbars in self.errorbars:
            data_line, caplines, barcollines = errorbars
            if errorbars.get_label() in self.results_dialog.mass_peaks_selected:
                alpha = 1
                min_y = min(min_y, errorbars.min_y)
                max_y = max(max_y, errorbars.max_y)
            else:
                alpha = 0
            data_line.set_alpha(alpha)
            for part in caplines:
                part.set_alpha(alpha)
            for part in barcollines:
                part.set_alpha(alpha)

        if min_y > max_y:
            min_y = 0
            max_y = 1
        self.axes.set_ylim(min_y, max_y)
        self.canvas.draw()