import matplotlib
from PyQt5.QtWidgets import QHBoxLayout, QDialog, QPushButton, QWidget, QVBoxLayout, QLabel, QCheckBox, QGridLayout, \
    QRadioButton
from PyQt5.QtCore import Qt

from models.data_key import DataKey

matplotlib.use('QT5Agg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar

from views.sample_tree import SampleTreeWidget
from utils import ui_utils


class StandardLineDialog(QDialog):
    def __init__(self, samples, configs):
        QDialog.__init__(self)

        self.samples = [sample for sample in samples if sample.is_standard]
        self.configuration_sbm = configs[0]
        self.configuration_non_sbm = configs[1]

        self.setWindowTitle("Standard line")
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
        top_bar.addWidget(QLabel("Hi?"))
        top_bar.addWidget(self.sbm_check_box, alignment=Qt.AlignCenter)
        # top_bar.addWidget(self.sample_flag_box, alignment=Qt.AlignRight)

        layout = QVBoxLayout()
        layout.addLayout(top_bar)
        layout.addWidget(self._create_standard_line_graph(samples))

        widget = QWidget()
        widget.setLayout(layout)
        return widget

    def _create_standard_line_graph(self, samples):

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
        if self.sbm_check_box.isChecked():
            self.plot_standard_line_graph(current_tree_item.spot, self.axes, self.configuration_sbm)
        else:
            self.plot_standard_line_graph(current_tree_item.spot, self.axes, self.configuration_non_sbm)

    def plot_standard_line_graph(self, spot, axis, config):
        axis.clear()
        axis.spines['top'].set_visible(False)
        axis.spines['right'].set_visible(False)
        xs = []
        xerrors = []
        ys = []
        yerrors = []
        if len(spot.data[config][DataKey.ACTIVITY_RATIOS]) == 0:
            pass
        else:
            for ratio in spot.data[config][DataKey.ACTIVITY_RATIOS]:
                if isinstance(ratio, str):
                    continue
                (x, dx), (y, dy) = ratio
                xs.append(x)
                xerrors.append(dx)
                ys.append(y)
                yerrors.append(dy)
        # TODO errors
        axis.scatter(xs, ys, label=spot.name)
        plt.errorbar(xs, ys, xerr=xerrors, yerr=yerrors)
        axis.set_xlabel("(238U)/(232Th)")
        axis.set_ylabel("(230Th)/(232Th)")
        plt.tight_layout()
        self.canvas.draw()
