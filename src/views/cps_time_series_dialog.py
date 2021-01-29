import matplotlib
from PyQt5.QtWidgets import QHBoxLayout, QDialog, QPushButton, QWidget, QVBoxLayout, QLabel, QCheckBox, QGridLayout, \
    QRadioButton
from PyQt5.QtCore import Qt

from models.row import DataKey

matplotlib.use('QT5Agg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar

from views.sample_tree import SampleTreeWidget
from utils import ui_utils


class cpsTimeSeriesDialog(QDialog):
    def __init__(self, samples):
        QDialog.__init__(self)

        self.samples = samples
        self.highlight_area = None

        self.setWindowTitle("cps measurements per cycle")
        self.setMinimumWidth(450)

        layout = QHBoxLayout()
        layout.addWidget(self._create_left_widget(self.samples))
        layout.addWidget(self._create_right_widget())
        self.setLayout(layout)

        self.sample_tree.set_samples(self.samples)

    def _create_right_widget(self):
        self.sample_tree = SampleTreeWidget()
        self.sample_tree.tree.currentItemChanged.connect(self.on_selected_sample_change)

        self.continue_button = QPushButton("Continue")
        self.continue_button.clicked.connect(self.accept)

        layout = QVBoxLayout()
        layout.addWidget(self.sample_tree)
        layout.addWidget(self.continue_button, alignment=Qt.AlignRight)

        widget = QWidget()
        widget.setLayout(layout)

        return widget

    def _create_left_widget(self, samples):
        self.sample_flag_box = QCheckBox("Flag spot")
        self.sample_flag_box.setChecked(False)

        self.sample_flag_box.stateChanged.connect(self.on_flag_point_state_changed)

        self.sbm_check_box = QCheckBox("Normalise to sbm")
        self.sbm_check_box.setChecked(False)

        self.sbm_check_box.stateChanged.connect(self.on_sbm_box_state_changed)

        top_bar = QHBoxLayout()
        top_bar.addWidget(QLabel("Sample and spot name"))
        top_bar.addWidget(self.sbm_check_box, alignment=Qt.AlignCenter)
        top_bar.addWidget(self.sample_flag_box, alignment=Qt.AlignRight)

        layout = QVBoxLayout()
        layout.addLayout(top_bar)
        layout.addWidget(self._create_cps_graph_and_point_selection(samples))

        widget = QWidget()
        widget.setLayout(layout)
        return widget

    def _create_cps_graph_and_point_selection(self, samples):

        graph_and_points = QWidget()
        layout = QVBoxLayout()

        fig = plt.figure()
        self.axes = plt.axes()

        graph_widget, self.canvas = ui_utils.create_figure_widget(fig, self)

        layout.addWidget(graph_widget)

        checkboxes = self.make_mass_check_boxes(samples)

        layout.addLayout(checkboxes)

        mini_background_graph = self.make_background_graph()

        layout.addLayout(mini_background_graph)

        graph_and_points.setLayout(layout)

        return graph_and_points

    #############
    ## Actions ##
    #############

    def on_selected_sample_change(self, current_tree_item, previous_tree_item):
        if current_tree_item is None:
            self.axis.clear()
            return

        if current_tree_item.is_sample:
            self.sample_flag_box.setVisible(False)
            return

        self.sample_flag_box.setVisible(True)
        self.sample_flag_box.setChecked(current_tree_item.spot.is_flagged)

        if self.sbm_check_box.isChecked():
            self.plot_cps_graph(current_tree_item.spot.massPeaks, self.axes, DataKey.SBM_NORMALISED)
        else:
            self.plot_cps_graph(current_tree_item.spot.massPeaks, self.axes, DataKey.COUNTS_PER_SECOND)

    def on_flag_point_state_changed(self):
        sample = self.sample_tree.tree.currentItem()
        sample.spot.is_flagged = self.sample_flag_box.isChecked()

    def on_sbm_box_state_changed(self):
        current_tree_item = self.sample_tree.tree.currentItem()
        if self.sbm_check_box.isChecked():
            self.plot_cps_graph(current_tree_item.spot.massPeaks, self.axes, DataKey.SBM_NORMALISED)
        else:
            self.plot_cps_graph(current_tree_item.spot.massPeaks, self.axes, DataKey.COUNTS_PER_SECOND)


    def plot_cps_graph(self, mass_peaks, axis, key):
        axis.clear()
        axis.spines['top'].set_visible(False)
        axis.spines['right'].set_visible(False)
        for massPeak in mass_peaks.values():
            for row in massPeak.rows:
                xs = [i for i in range(len(row.data[key]))]
                ys = [value for value in row.data[key]]
            axis.plot(xs, ys, label = massPeak.mpName)
            plt.legend(loc = "upper left")
        axis.set_xlabel("Spot number")
        axis.set_ylabel(key)
        plt.tight_layout()
        self.canvas.draw()

    def make_mass_check_boxes(self, samples):

        for sample in samples:
            for spot in sample.spots:
                masses = spot.mpNames

        checkbox_layout = QGridLayout()

        for i, mass in enumerate(masses):
            box = QCheckBox(mass)
            checkbox_layout.addWidget(box, i // 3, i % 3)

        return checkbox_layout



    def make_background_graph(self):
        pass
