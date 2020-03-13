from PyQt5.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel, QListWidget, QGridLayout, QTreeWidget, \
    QTreeWidgetItem, QPushButton, QFileDialog


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
        self.tree_widget = QTreeWidget()
        self.tree_widget.setHeaderLabel("Samples")
        #self.list_widget.currentItemChanged.connect(self.on_selected_sample_change)

        self.file_list = QTreeWidget()
        self.file_list.setHeaderLabel("Files imported")


        self.import_button = QPushButton("Import data file")
        self.import_button.clicked.connect(self.on_import_samples_clicked)

        layout = QVBoxLayout()
        layout.addWidget(self.file_list)
        layout.addWidget(self.tree_widget)
        layout.addWidget(self.import_button)

        lhs_widget = QWidget()
        lhs_widget.setLayout(layout)
        return lhs_widget

    def create_rhs(self):
        self.info_box_widget = QWidget()
        self.rhs_title = QLabel()
        info_box = QLabel("sample information")
        button_widget_rhs = self.create_rhs_buttons()

        layout = QVBoxLayout()
        layout.addWidget(self.rhs_title)
        layout.addWidget(info_box)
        layout.addWidget(button_widget_rhs)
        self.info_box_widget.setLayout(layout)
        return self.info_box_widget

    def create_rhs_buttons(self):
        layout = QHBoxLayout()

        button_widget_rhs = QWidget()
        button_widget_rhs.setLayout(layout)
        return button_widget_rhs

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
        self.tree_widget.clear()
        self.file_list.clear()

        for file in files:
            QTreeWidgetItem(self.file_list, [file])

        for sample in samples:
            sample_tree_item = QTreeWidgetItem(self.tree_widget, [sample.name])
            sample_tree_item.sample = sample
            sample_tree_item.is_sample = True
            for spot in sample.spots:
                spot_tree_item = QTreeWidgetItem(sample_tree_item, [spot.id])
                spot_tree_item.spot = spot
                spot_tree_item.is_sample = False

    # def on_selected_sample_change(self, current_sample_item, previous_sample_item):
    #     is_selected = current_sample_item is not None
    #     self.edit_sample_button.setEnabled(is_selected)
    #     self.delete_sample_button.setEnabled(is_selected)
    #     if is_selected:
    #         self.rhs_title.setText("Sample: " + current_sample_item.sample.name)
    #     else:
    #         self.rhs_title.setText("")