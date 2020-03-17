from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel, QListWidget, QGridLayout, QTreeWidget, \
    QTreeWidgetItem, QPushButton, QFileDialog, QGroupBox

from views.sample_info_box import SampleInfoBox
from views.spot_info_box import SpotInfoBox

class SamplesOverview(QWidget):
    def __init__(self, model):
        QWidget.__init__(self)

        self.model = model
        model.signals.sample_list_updated.connect(self.on_sample_list_updated)

        gridLayout = QGridLayout()
        self.setLayout(gridLayout)

        gridLayout.addWidget(self.create_lhs(), 0, 0)
        gridLayout.addWidget(self.create_rhs(), 0, 1)
        gridLayout.setColumnStretch(0, 1)
        gridLayout.setColumnStretch(1, 1)

    def create_lhs(self):
        self.sample_tree = QTreeWidget()
        self.sample_tree.setHeaderLabel("Samples")
        self.sample_tree.currentItemChanged.connect(self.on_selected_sample_change)

        self.file_list = QTreeWidget()
        self.file_list.setHeaderLabel("Files imported")

        self.import_button = QPushButton("Import data file")
        self.import_button.clicked.connect(self.on_import_samples_clicked)

        layout = QVBoxLayout()
        layout.addWidget(self.file_list,1)
        layout.addWidget(self.sample_tree, 3)
        layout.addWidget(self.import_button)

        lhs_widget = QWidget()
        lhs_widget.setLayout(layout)
        return lhs_widget

    def create_rhs(self):
        self.spot_box = SpotInfoBox()
        self.spot_box.setVisible(False)
        self.sample_box = SampleInfoBox()
        self.sample_box.setVisible(False)

        self.process_button = QPushButton("Process data")
        self.process_button.setVisible(False)
        self.process_button.clicked.connect(self.on_process_button_clicked)

        layout = QVBoxLayout()
        layout.addWidget(self.spot_box)
        layout.addWidget(self.sample_box)
        layout.addWidget(self.process_button,0, Qt.AlignBottom)

        rhs_widget = QWidget()
        rhs_widget.setLayout(layout)
        return rhs_widget

    #############
    ## Actions ##
    #############

    def on_import_samples_clicked(self):
        # popup to be made for now outputs are filename,
        file_name, _ = QFileDialog.getOpenFileName(self, "Select data file", "", "All Files (*);;CSV Files (*.csv)")
        if not file_name:
            return
        replace = False
        # model needs to do the importing
        self.model.import_samples(file_name, replace)

    def on_sample_list_updated(self, samples, files):
        self.sample_tree.clear()
        self.file_list.clear()
        self.process_button.setVisible(True)

        for file in files:
            QTreeWidgetItem(self.file_list, [file])

        for sample in samples:
            sample_tree_item = QTreeWidgetItem(self.sample_tree, [sample.name])
            sample_tree_item.sample = sample
            sample_tree_item.is_sample = True
            for spot in sample.spots:
                spot_tree_item = QTreeWidgetItem(sample_tree_item, [spot.id])
                spot_tree_item.spot = spot
                spot_tree_item.is_sample = False

    def on_selected_sample_change(self, current_tree_item, previous_tree_item):
        if current_tree_item is None:
            self.sample_box.setVisible(False)
            self.spot_box.setVisible(False)
            return
        self.sample_box.setVisible(current_tree_item.is_sample)
        self.spot_box.setVisible(not current_tree_item.is_sample)

        if current_tree_item.is_sample:
            self.sample_box.display_sample(current_tree_item.sample)
        else:
            self.spot_box.display_spot(current_tree_item.spot)

    def on_process_button_clicked(self):
        self.model.process_samples()
