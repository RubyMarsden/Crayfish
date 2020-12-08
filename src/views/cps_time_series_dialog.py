import matplotlib
from PyQt5.QtWidgets import QHBoxLayout, QDialog, QPushButton, QWidget, QVBoxLayout, QLabel, QCheckBox, QGridLayout
from PyQt5.QtCore import Qt

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


    def _create_left_widget(self, samples):
        self.point_flag_box = QCheckBox("Flag point")
        self.point_flag_box.setChecked(False)

        self.point_flag_box.stateChanged.connect(self.on_flag_point_state_changed)

        top_bar = QHBoxLayout()
        top_bar.addWidget(QLabel("Sample and spot name"))
        top_bar.addWidget(self.point_flag_box, alignment=Qt.AlignRight)

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
        self.axis = fig.add_subplot(2, 1, 1)
        self.all_axis = fig.add_subplot(2, 1, 2)

        # self.create_all_sbm_time_series(self.samples, self.all_axis)

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
            self.point_flag_box.setVisible(False)
            return

        self.point_flag_box.setVisible(True)
        # self.sample_flag_box.setChecked(current_tree_item.spot.is_flagged)

        self.plot_cps_graph(current_tree_item.spot.sbm_time_series, self.axis)

        # self.highlight_spot_sbm(current_tree_item.spot)


    def on_flag_point_state_changed(self):
        sample = self.sample_tree.tree.currentItem()
        # sample.spot.is_flagged = self.point_flag_box.isChecked()


    def plot_cps_graph(self, data, axis):
        pass

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
