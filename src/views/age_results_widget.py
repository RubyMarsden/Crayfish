import matplotlib
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QHBoxLayout, QDialog, QPushButton, QWidget, QVBoxLayout, QLabel

matplotlib.use('QT5Agg')
import matplotlib.pyplot as plt

from models.data_key import DataKey
from utils import ui_utils


class AgeResultsWidget(QWidget):
    def __init__(self, results_dialog):
        QWidget.__init__(self)

        self.results_dialog = results_dialog

        layout = QHBoxLayout()
        layout.addLayout(self._create_widget())
        self.setLayout(layout)

        results_dialog.sample_tree.tree.currentItemChanged.connect(lambda i, j: self.replot_graph())
        results_dialog.configuration_changed.connect(self.replot_graph)

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

    ###############
    ### Actions ###
    ###############

    def replot_graph(self):
        current_item = self.results_dialog.sample_tree.tree.currentItem()
        config = self.results_dialog.configuration_widget.current_config
        if config and current_item:
            self.plot_cps_graph(current_item.spot, config)

    def plot_cps_graph(self, spot, config):
        axis = self.axes
        axis.clear()
        if spot is None:
            return
        axis.spines['top'].set_visible(False)
        axis.spines['right'].set_visible(False)
        xs = []
        ys = []
        errors = []
        if DataKey.AGES not in spot.data[config]:
            # TODO plot words on graph
            return
        ages = spot.data[config][DataKey.AGES]
        if len(ages) != 0:
            for i, age in enumerate(ages):
                if isinstance(age, str):
                    continue
                x = i + 1
                y, dy = age
                xs.append(x)
                if y is None:
                    ys.append(0)
                    errors.append(0)
                else:
                    ys.append(y)
                    errors.append(dy)
        else:
            # TODO plot some text
            return
        weighted_age, age_st_dev = spot.data[config][DataKey.WEIGHTED_AGE]
        if isinstance(weighted_age, str):
            string = "No weighted age"
        else:
            string = f"Weighted age: {weighted_age:.0f}, 1σ: {age_st_dev:.0f}"

        axis.errorbar(xs, ys, yerr=errors, linestyle="none", marker='o')
        axis.text(0.5, 1, string, transform=axis.transAxes, horizontalalignment="center")
        axis.set_xlabel("Scan number")
        axis.set_ylabel("Age (ka)")
        self.canvas.draw()
