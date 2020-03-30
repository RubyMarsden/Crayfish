import matplotlib
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QWidget, QHBoxLayout, QLabel
from matplotlib.backend_bases import NavigationToolbar2

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

        layout = QVBoxLayout()
        layout.addWidget(self._create_top_widget())
        layout.addWidget(self._create_bottom_widget())
        self.setLayout(layout)

    def _create_top_widget(self):
        self.sample_tree = SampleTreeWidget()
        self.sample_tree.set_samples(self.samples)
        self.sample_tree.currentItemChanged.connect(self.on_selected_sample_change)

        layout = QHBoxLayout()
        layout.addWidget(self._create_spot_sbm_graph())
        layout.addWidget(self.sample_tree)

        widget = QWidget()
        widget.setLayout(layout)

        return widget

    def _create_bottom_widget(self):
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Title"))
        layout.addWidget(self._create_all_sbm_graph())

        widget = QWidget()
        widget.setLayout(layout)
        return widget

    def _create_spot_sbm_graph(self):
        fig, self.axis = plt.subplots()
        # plt.xlim(*self._default_xlim)
        # plt.ylim(*self._default_ylim)

        # plot
        self.spot_canvas = FigureCanvas(fig)
        toolbar = CustomNavigationToolbar(self.spot_canvas, self)

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.spot_canvas)
        layout.addWidget(toolbar)

        widget = QWidget()
        widget.setLayout(layout)
        return widget

    def _create_all_sbm_graph(self):
        fig, self.all_axis = plt.subplots()

        self.create_all_sbm_time_series(self.samples, self.all_axis)

        # plot
        self.all_canvas = FigureCanvas(fig)
        toolbar = CustomNavigationToolbar(self.all_canvas, self)

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.all_canvas)
        layout.addWidget(toolbar)

        widget = QWidget()
        widget.setLayout(layout)
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
        axis.set_xlabel("Time (s)")
        axis.set_ylabel("SBM (cps)")
        plt.tight_layout()
        self.spot_canvas.draw()

    def on_selected_sample_change(self, current_tree_item, previous_tree_item):
        if current_tree_item is None:
            self.axis.clear()
            return

        if current_tree_item.is_sample:
            return

        self.plot_time_series(current_tree_item.spot.sbm_time_series, self.axis)

        self.highlight_spot_sbm(current_tree_item.spot)

    def create_all_sbm_time_series(self, samples, axis):
        axis.spines['top'].set_visible(False)
        axis.spines['right'].set_visible(False)
        axis.set_xlabel("Time (s)")
        axis.set_ylabel("SBM (cps)")
        plt.tight_layout()

        all_spots = []
        for sample in samples:
            all_spots.extend(sample.spots)
        sorted_spots = sorted(all_spots, key= lambda spot: spot.date_and_time)

        self.start_end_time = {}
        time = 0
        interspot_time = 100
        for spot in sorted_spots:
            xs, ys = zip(*spot.sbm_time_series)
            shifted_xs = [x + time for x in xs]
            axis.plot(shifted_xs, ys, color = 'b')
            self.start_end_time[spot] = time, time + spot.count_time_duration
            time += spot.count_time_duration + interspot_time


        axis.set_xlim(0, time)

    def highlight_spot_sbm(self, spot):
        if self.highlight_area is not None:
            self.highlight_area.remove()
        print(spot.name)
        start_time, end_time = self.start_end_time[spot]
        self.highlight_area = self.all_axis.fill_betweenx([0, 300000], start_time, end_time, facecolor='#ff000080')
        self.all_canvas.draw()

#############
## Hacking ##
#############

def _repurpose_toolbar_buttons():
    new_tool_items = []

    # take out back and forward items and saves them
    back_item = None
    forward_item = None
    for item in NavigationToolbar2.toolitems:
        if item[0] == "Back":
            back_item = item
        elif item[0] == "Forward":
            forward_item = item
        else:
            new_tool_items.append(item)

    # new method for back and forward items
    if back_item is None or forward_item is None:
        raise Exception("Matplotlib API has changed")

    back_item = list(back_item)
    back_item[3] = "previous_spot"
    forward_item = list(forward_item)
    forward_item[3] = "next_spot"

    new_tool_items.extend([back_item, forward_item])

    return new_tool_items


class CustomNavigationToolbar(NavigationToolbar):
    # Use the standard toolbar items + download button
    toolitems = _repurpose_toolbar_buttons()

    def previous_spot(self):
        print("previous")

    def next_spot(self):
        print("next")
