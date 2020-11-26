from PyQt5.QtWidgets import QTreeWidget, QTreeWidgetItem, QWidget, QPushButton, QHBoxLayout, QVBoxLayout


class SampleTreeWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.tree = QTreeWidget()

        self.tree.currentItemChanged.connect(self._on_selected_sample_change)

        self.tree.setHeaderLabel("Samples")
        self.buttons = self._create_next_and_back_buttons()

        layout = QVBoxLayout()
        layout.addWidget(self.tree)
        layout.addWidget(self.buttons)

        self.setLayout(layout)

    def set_samples(self, samples):
        self.tree.clear()
        for sample in samples:
            sample_tree_item = QTreeWidgetItem(self.tree, [sample.name])
            sample_tree_item.sample = sample
            sample_tree_item.is_sample = True
            for spot in sample.spots:
                spot_tree_item = QTreeWidgetItem(sample_tree_item, [spot.id])
                spot_tree_item.spot = spot
                spot_tree_item.is_sample = False
        self.next_item_button.setDisabled(False)
        self.back_item_button.setDisabled(False)
        self.select_first_spot()

    def select_first_spot(self):
        first_sample = self.tree.topLevelItem(0)
        first_spot = first_sample.child(0)
        self.tree.setCurrentItem(first_spot)

    def _create_next_and_back_buttons(self):

        self.next_item_button = QPushButton("Next")
        self.next_item_button.clicked.connect(self.on_next_item_clicked)
        self.back_item_button = QPushButton("Back")
        self.back_item_button.clicked.connect(self.on_back_item_clicked)

        self.next_item_button.setDisabled(True)
        self.back_item_button.setDisabled(True)

        layout = QHBoxLayout()
        layout.addWidget(self.back_item_button)
        layout.addWidget(self.next_item_button)

        widget = QWidget()
        widget.setLayout(layout)

        return widget

    #######
    #Actions
    #######

    def on_next_item_clicked(self):
        self.back_item_button.setEnabled(True)
        current_item = self.tree.currentItem()
        next_item = self.tree.itemBelow(current_item)
        if current_item.is_sample and current_item.childCount() > 0:
            next_item = current_item.child(0)

        self.tree.setCurrentItem(next_item)

    def on_back_item_clicked(self):
        self.next_item_button.setEnabled(True)
        current_item = self.tree.currentItem()
        previous_item = self.tree.itemAbove(current_item)
        self.tree.setCurrentItem(previous_item)

    def _on_selected_sample_change(self, current_tree_item, previous_tree_item):
        if current_tree_item is None:
            return

        next_item = self.tree.itemBelow(current_tree_item)
        self.next_item_button.setDisabled(next_item is None)

        previous_item = self.tree.itemAbove(current_tree_item)
        self.back_item_button.setDisabled(previous_item is None)