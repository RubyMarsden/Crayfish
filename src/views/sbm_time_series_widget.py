import matplotlib
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QVBoxLayout, QWidget, QHBoxLayout, QLabel, QCheckBox

from utils import ui_utils
from views.sample_tree import SampleTreeWidget

matplotlib.use('QT5Agg')
import matplotlib.pyplot as plt


class SBMTimeSeriesWidget(QWidget):
    def __init__(self, results_dialog):
        QWidget.__init__(self)

        self.results_dialog = results_dialog

        self.samples = self.results_dialog.samples
        self.highlight_area = None

        self.setWindowTitle("SBM time series")
        self.setMinimumWidth(450)

        layout = QHBoxLayout()
        layout.addLayout(self._create_left_widget())
        self.setLayout(layout)

        self.results_dialog.sample_tree.tree.currentItemChanged.connect(self.on_selected_sample_change)

    def _create_left_widget(self):
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Secondary beam monitor"))
        layout.addWidget(self._create_sbm_graphs())

        return layout

    def _create_sbm_graphs(self):

        fig = plt.figure()
        self.axis = fig.add_subplot(2, 1, 1)
        self.all_axis = fig.add_subplot(2, 1, 2)

        self.create_all_sbm_time_series(self.samples, self.all_axis)

        widget, self.canvas = ui_utils.create_figure_widget(fig, self)

        return widget

    #############
    ## Actions ##
    #############

    def plot_time_series(self, time_series, axis):
        axis.clear()
        axis.spines['top'].set_visible(False)
        axis.spines['right'].set_visible(False)
        xs, ys = zip(*time_series)
        axis.plot(xs, ys)
        axis.set_xlabel("Relative spot time (s)")
        axis.set_ylabel("SBM (cps)")
        plt.tight_layout()
        self.canvas.draw()

    def on_selected_sample_change(self, current_tree_item, previous_tree_item):

        if current_tree_item is None or current_tree_item.is_sample:
            self.axis.clear()
            return

        self.plot_time_series(current_tree_item.spot.sbm_time_series, self.axis)

        self.highlight_spot_sbm(current_tree_item.spot)

    def create_all_sbm_time_series(self, samples, axis):
        axis.spines['top'].set_visible(False)
        axis.spines['right'].set_visible(False)
        axis.set_xlabel("Time (h)")
        axis.set_ylabel("SBM (cps)")
        plt.tight_layout()

        all_spots = []
        for sample in samples:
            all_spots.extend(sample.spots)
        sorted_spots = sorted(all_spots, key=lambda spot: spot.date_and_time)

        self.start_end_time = {}
        time = 0
        inter_spot_time = 100
        for spot in sorted_spots:
            xs, ys = zip(*spot.sbm_time_series)
            output_xs = [(x + time) / 3600 for x in xs]
            axis.plot(output_xs, ys, color='b')
            self.start_end_time[spot] = time, time + spot.count_time_duration
            time += spot.count_time_duration + inter_spot_time

        axis.set_xlim(0, time / 3600)

    def highlight_spot_sbm(self, spot):
        if self.highlight_area is not None:
            self.highlight_area.remove()
        start_time, end_time = self.start_end_time[spot]
        self.highlight_area = self.all_axis.fill_betweenx([0, 300000], start_time / 3600, end_time / 3600,
                                                          facecolor='#ff000080')
        self.canvas.draw()
