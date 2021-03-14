import math

import matplotlib
from PyQt5.QtWidgets import QVBoxLayout, QWidget, QHBoxLayout, QLabel, QCheckBox
from matplotlib.gridspec import GridSpec

from utils import ui_utils

matplotlib.use('QT5Agg')
import matplotlib.pyplot as plt


class SBMTimeSeriesWidget(QWidget):
    def __init__(self, results_dialog):
        QWidget.__init__(self)

        self.results_dialog = results_dialog

        self.samples = self.results_dialog.samples
        self.highlight_area = None

        self.start_end_time = None
        self.max_sbm_count = None

        self.setWindowTitle("SBM time series")
        self.setMinimumWidth(450)

        layout = QHBoxLayout()
        layout.addLayout(self._create_left_widget())
        self.setLayout(layout)

        self.results_dialog.sample_tree.tree.currentItemChanged.connect(lambda x, y: self.update_individual_spot_plot())

    def _create_left_widget(self):
        layout = QVBoxLayout()
        layout.addLayout(self._create_title_bar())
        layout.addWidget(self._create_sbm_graphs())

        return layout

    def _create_title_bar(self):
        layout = QHBoxLayout()
        title_widget = QLabel("Secondary beam monitor")
        self.show_spot_checkbox = QCheckBox("Spot highlighting")
        self.show_spot_checkbox.setChecked(True)

        self.show_spot_checkbox.stateChanged.connect(self.update_individual_spot_plot)
        layout.addWidget(title_widget)
        layout.addWidget(self.show_spot_checkbox)

        return layout

    def _create_sbm_graphs(self):
        self.fig = plt.figure()

        self.spot_visible_grid_spec = GridSpec(2, 1)
        self.spot_invisible_grid_spec = GridSpec(1, 1)
        self.spot_axis = self.fig.add_subplot(self.spot_visible_grid_spec[0])
        self.all_axis = self.fig.add_subplot(self.spot_visible_grid_spec[1])

        self.create_all_sbm_time_series(self.samples, self.all_axis)

        widget, self.canvas = ui_utils.create_figure_widget(self.fig, self)

        return widget

    #############
    ## Actions ##
    #############

    def update_individual_spot_plot(self):
        if self.highlight_area is not None:
            self.highlight_area.remove()
            self.highlight_area = None

        show_spot = self.show_spot_checkbox.isChecked()
        grid_spec = self.spot_visible_grid_spec[1] if show_spot else self.spot_invisible_grid_spec[0]
        self.all_axis.set_position(grid_spec.get_position(self.fig))
        self.spot_axis.set_visible(show_spot)

        spot = self.results_dialog.sample_tree.current_spot()

        if not show_spot or spot is None:
            self.spot_axis.clear()
        else:
            self.plot_individual_spot_time_series(spot.sbm_time_series, self.spot_axis)
            self.highlight_spot_sbm(spot)

        self.canvas.draw()

    def create_all_sbm_time_series(self, samples, axis):
        axis.spines['top'].set_visible(False)
        axis.spines['right'].set_visible(False)
        axis.set_xlabel("Time (h)")
        axis.set_ylabel("SBM (cps)")
        plt.tight_layout()

        all_spots = []
        for sample in samples:
            all_spots.extend(sample.spots)
        sorted_spots = sorted(all_spots, key=lambda s: s.date_and_time)

        self.start_end_time = {}
        self.max_sbm_count = 0
        time = 0
        inter_spot_time = 100
        for spot in sorted_spots:
            xs, ys = zip(*spot.sbm_time_series)
            output_xs = [(x + time) / 3600 for x in xs]
            axis.plot(output_xs, ys, color='b')

            self.start_end_time[spot] = time, time + spot.count_time_duration
            self.max_sbm_count = max(self.max_sbm_count, max(ys))
            time += spot.count_time_duration + inter_spot_time

        self.max_sbm_count = math.ceil(self.max_sbm_count/1000) * 1000
        axis.set_xlim(0, time / 3600)

    def highlight_spot_sbm(self, spot):
        start_time, end_time = self.start_end_time[spot]
        self.highlight_area = self.all_axis.fill_betweenx([0, self.max_sbm_count], start_time / 3600, end_time / 3600,
                                                          facecolor='#ff000080')


    def plot_individual_spot_time_series(self, time_series, axis):
        axis.clear()
        axis.spines['top'].set_visible(False)
        axis.spines['right'].set_visible(False)
        xs, ys = zip(*time_series)
        axis.plot(xs, ys)
        axis.set_xlabel("Relative spot time (s)")
        axis.set_ylabel("SBM (cps)")
        plt.tight_layout()
