import matplotlib
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QWidget, QHBoxLayout, QLabel, QPushButton, QCheckBox
from matplotlib.backend_bases import NavigationToolbar2

from utils import ui_utils
from views.sample_tree import SampleTreeWidget

matplotlib.use('QT5Agg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar


class SBMTimeSeriesDialog(QDialog):
    def __init__(self, samples):
        QDialog.__init__(self)

        self.samples = samples
        self.highlight_area = None

        self.setWindowTitle("SBM time series")
        self.setMinimumWidth(450)

        layout = QHBoxLayout()
        layout.addWidget(self._create_left_widget())
        layout.addWidget(self._create_right_widget())
        self.setLayout(layout)


    def _create_right_widget(self):
        self.sample_tree = SampleTreeWidget()
        self.sample_tree.set_samples(self.samples)
        self.sample_tree.tree.currentItemChanged.connect(self.on_selected_sample_change)


        self.continue_button = QPushButton("Continue")
        self.continue_button.clicked.connect(self.accept)

        layout = QVBoxLayout()
        layout.addWidget(self.sample_tree)
        layout.addWidget(self.continue_button, alignment=Qt.AlignRight)

        widget = QWidget()
        widget.setLayout(layout)

        return widget


    def _create_left_widget(self):
        self.sample_flag_box = QCheckBox("Flag spot")
        self.sample_flag_box.setChecked(False)

        self.sample_flag_box.stateChanged.connect(self.on_flag_spot_state_changed)

        top_bar = QHBoxLayout()
        top_bar.addWidget(QLabel("Secondary beam monitor"))
        top_bar.addWidget(self.sample_flag_box, alignment= Qt.AlignRight)

        layout = QVBoxLayout()
        layout.addLayout(top_bar)
        layout.addWidget(self._create_sbm_graphs())

        widget = QWidget()
        widget.setLayout(layout)
        return widget

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
        if current_tree_item is None:
            self.axis.clear()
            return

        if current_tree_item.is_sample:
            self.sample_flag_box.setVisible(False)
            return

        self.sample_flag_box.setVisible(True)
        self.sample_flag_box.setChecked(current_tree_item.spot.is_flagged)

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
        interspot_time = 100
        for spot in sorted_spots:
            xs, ys = zip(*spot.sbm_time_series)
            output_xs = [(x + time) / 3600 for x in xs]
            axis.plot(output_xs, ys, color='b')
            self.start_end_time[spot] = time, time + spot.count_time_duration
            time += spot.count_time_duration + interspot_time

        axis.set_xlim(0, time / 3600)

    def highlight_spot_sbm(self, spot):
        if self.highlight_area is not None:
            self.highlight_area.remove()
        start_time, end_time = self.start_end_time[spot]
        self.highlight_area = self.all_axis.fill_betweenx([0, 300000], start_time / 3600, end_time / 3600,
                                                          facecolor='#ff000080')
        self.canvas.draw()



    def on_flag_spot_state_changed(self):
        sample = self.sample_tree.tree.currentItem()
        sample.spot.is_flagged = self.sample_flag_box.isChecked()

