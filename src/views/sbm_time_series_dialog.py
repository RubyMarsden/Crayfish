import matplotlib
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
        first_sample = self.sample_tree.topLevelItem(0)
        first_spot = first_sample.child(0)
        self.sample_tree.setCurrentItem(first_spot)

    def _create_right_widget(self):
        self.sample_tree = SampleTreeWidget()
        self.sample_tree.set_samples(self.samples)
        self.sample_tree.currentItemChanged.connect(self.on_selected_sample_change)

        self.buttons = self._create_next_and_back_buttons()

        self.sample_flag_box = QCheckBox("Flag spot")
        self.sample_flag_box.setChecked(False)

        self.sample_flag_box.stateChanged.connect(self.on_flag_spot_state_changed)

        layout = QVBoxLayout()
        layout.addWidget(self.sample_tree)
        layout.addWidget(self.buttons)
        layout.addWidget(self.sample_flag_box)

        widget = QWidget()
        widget.setLayout(layout)

        return widget

    def _create_next_and_back_buttons(self):

        self.next_item_button = QPushButton("Next")
        self.next_item_button.clicked.connect(self.on_next_item_clicked)
        self.back_item_button = QPushButton("Back")
        self.back_item_button.clicked.connect(self.on_back_item_clicked)

        layout = QHBoxLayout()
        layout.addWidget(self.back_item_button)
        layout.addWidget(self.next_item_button)

        widget = QWidget()
        widget.setLayout(layout)

        return widget

    def _create_left_widget(self):
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Secondary beam monitor"))
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

        next_item = self.sample_tree.itemBelow(current_tree_item)
        self.next_item_button.setDisabled(next_item is None)

        previous_item = self.sample_tree.itemAbove(current_tree_item)
        self.back_item_button.setDisabled(previous_item is None)

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

    def on_next_item_clicked(self):
        self.back_item_button.setEnabled(True)
        current_item = self.sample_tree.currentItem()
        next_item = self.sample_tree.itemBelow(current_item)
        if current_item.is_sample and current_item.childCount() > 0:
            next_item = current_item.child(0)

        self.sample_tree.setCurrentItem(next_item)

    def on_back_item_clicked(self):
        self.next_item_button.setEnabled(True)
        current_item = self.sample_tree.currentItem()
        previous_item = self.sample_tree.itemAbove(current_item)
        self.sample_tree.setCurrentItem(previous_item)

    def on_flag_spot_state_changed(self):
        sample = self.sample_tree.currentItem()
        sample.spot.is_flagged = self.sample_flag_box.isChecked()

