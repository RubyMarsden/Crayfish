import matplotlib
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QWidget

matplotlib.use('QT5Agg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar


class SBMTimeSeriesDialog(QDialog):
    def __init__(self, samples):
        QDialog.__init__(self)

        self.samples = samples

        self.setWindowTitle("SBM time series")
        self.setMinimumWidth(350)

        layout = QVBoxLayout()
        layout.addWidget(self.createGraph())
        self.setLayout(layout)

        self.plot_time_series(samples[0].spots[0].sbm_time_series)

    def createGraph(self):

        fig, self.axis = plt.subplots()
        #plt.xlim(*self._default_xlim)
        #plt.ylim(*self._default_ylim)
        #plt.tight_layout(rect=[0.05, 0.08, 1, 0.95])


        # plot
        self.canvas = FigureCanvas(fig)
        toolbar = NavigationToolbar(self.canvas, self)

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.canvas)
        layout.addWidget(toolbar)

        widget = QWidget()
        widget.setLayout(layout)
        return widget

    def plot_time_series(self, time_series):
        self.axis.clear()
        self.axis.spines['top'].set_visible(False)
        self.axis.spines['right'].set_visible(False)
        xs, ys = zip(*time_series)
        self.axis.plot(xs, ys)
