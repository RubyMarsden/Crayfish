import matplotlib
from PyQt5.QtWidgets import QHBoxLayout, QPushButton, QWidget, QVBoxLayout, QLabel, QCheckBox
from PyQt5.QtCore import Qt

from models.data_key import DataKey

matplotlib.use('QT5Agg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar

from views.sample_tree import SampleTreeWidget
from utils import ui_utils


class StandardLineWidget(QWidget):
    def __init__(self, configs, samples):
        QWidget.__init__(self)

        self.samples = [sample for sample in samples if sample.is_standard]
        self.configuration_sbm = configs[0]
        self.configuration_non_sbm = configs[1]

        self.setWindowTitle("Standard line")
        self.setMinimumWidth(450)

        layout = QHBoxLayout()
        layout.addWidget(self._create_left_widget(self.samples, configs[0]))
        layout.addWidget(self._create_right_widget())
        self.setLayout(layout)

        self.sample_tree.set_samples(self.samples)

    def _create_right_widget(self):
        self.sample_tree = SampleTreeWidget()
        self.sample_tree.tree.currentItemChanged.connect(self.on_selected_sample_change)

        self.continue_button = QPushButton("Continue")
        # self.continue_button.clicked.connect(self.accept)

        layout = QVBoxLayout()
        layout.addWidget(self.sample_tree)
        layout.addWidget(self.continue_button, alignment=Qt.AlignRight)

        widget = QWidget()
        widget.setLayout(layout)

        return widget

    def _create_left_widget(self, samples, config):
        self.sbm_check_box = QCheckBox("Normalise to sbm")
        self.sbm_check_box.setChecked(False)

        top_bar = QHBoxLayout()
        top_bar.addWidget(QLabel("Standard line"))
        top_bar.addWidget(self.sbm_check_box, alignment=Qt.AlignCenter)

        layout = QVBoxLayout()
        layout.addLayout(top_bar)
        layout.addWidget(self._create_standard_line_graph(samples, config))
        self.plot_standard_line_graph(samples, self.axes, config)

        widget = QWidget()
        widget.setLayout(layout)
        return widget

    def _create_standard_line_graph(self, samples, config):

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
        #     self.plot_standard_line_graph(current_tree_item.spot, self.axes, self.configuration_sbm)
        # else:
        #     self.plot_standard_line_graph(current_tree_item.spot, self.axes, self.configuration_non_sbm)

    def plot_standard_line_graph(self, samples, axis, config):
        axis.clear()
        axis.spines['top'].set_visible(False)
        axis.spines['right'].set_visible(False)
        xs = []
        x_errors = []
        ys = []
        y_errors = []
        for sample in samples:
            for spot in sample.spots:
                if len(spot.data[config][DataKey.ACTIVITY_RATIOS]) == 0:
                    pass
                else:
                    for ratio in spot.data[config][DataKey.ACTIVITY_RATIOS]:
                        if isinstance(ratio, str):
                            continue
                        (x, dx), (y, dy) = ratio
                        xs.append(x)
                        x_errors.append(dx)
                        ys.append(y)
                        y_errors.append(dy)
        plt.errorbar(xs, ys, xerr=x_errors, yerr=y_errors, linestyle='none', marker='o')
        axis.set_xlabel("(238U)/(232Th)")
        axis.set_ylabel("(230Th)/(232Th)")
        plt.tight_layout()
        self.canvas.draw()
