import matplotlib
from PyQt5.QtWidgets import QHBoxLayout, QDialog, QPushButton, QWidget, QVBoxLayout, QLabel, QCheckBox, QGridLayout, \
    QRadioButton
from PyQt5.QtCore import Qt


matplotlib.use('QT5Agg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar

from views.sample_tree import SampleTreeWidget
from utils import ui_utils


class AgeDialog(QDialog):
    def __init__(self, samples):
        QDialog.__init__(self)

        self.samples = [sample for sample in samples if not sample.is_standard]

        self.setWindowTitle("Ages")
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
        # self.sample_flag_box = QCheckBox("Flag spot")
        # self.sample_flag_box.setChecked(False)

        # self.sample_flag_box.stateChanged.connect(self.on_flag_point_state_changed)

        self.sbm_check_box = QCheckBox("Normalise to sbm")
        self.sbm_check_box.setChecked(False)

        # self.sbm_check_box.stateChanged.connect(self.on_sbm_box_state_changed)

        top_bar = QHBoxLayout()
        top_bar.addWidget(QLabel("Sample and spot name"))
        top_bar.addWidget(self.sbm_check_box, alignment=Qt.AlignCenter)
        # top_bar.addWidget(self.sample_flag_box, alignment=Qt.AlignRight)

        layout = QVBoxLayout()
        layout.addLayout(top_bar)
        layout.addWidget(self._create_age_graph_and_point_selection(samples))

        widget = QWidget()
        widget.setLayout(layout)
        return widget

    def _create_age_graph_and_point_selection(self, samples):

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

    def on_selected_sample_change(self, current_tree_item, previous_tree_item):
        if current_tree_item is None:
            self.axis.clear()
            return
        #
        # if current_tree_item.is_sample:
        #     self.sample_flag_box.setVisible(False)
        #     return
        #
        # self.sample_flag_box.setVisible(True)
        # self.sample_flag_box.setChecked(current_tree_item.spot.is_flagged)
        #
        # if self.sbm_check_box.isChecked():
        self.plot_cps_graph(current_tree_item.spot, self.axes)
        # else:
        #     self.plot_cps_graph(current_tree_item.spot.massPeaks, self.axes, "counts normalised to time")
        pass

    def plot_cps_graph(self, spot, axis):
        axis.clear()
        axis.spines['top'].set_visible(False)
        axis.spines['right'].set_visible(False)
        xs = []
        ys = []
        errors = []

        for i, age in enumerate(spot.data["ages"]):
            x = i + 1
            y, dy = age
            xs.append(x)
            if y is None:
                ys.append(0)
                errors.append(0)
            else:
                ys.append(y)
                errors.append(dy)
        # TODO errors
        axis.scatter(xs, ys, label=spot.name)
        plt.errorbar(xs, ys, yerr=errors)
        axis.set_xlabel("Scan number")
        axis.set_ylabel("Age (ka)")
        plt.tight_layout()
        self.canvas.draw()
