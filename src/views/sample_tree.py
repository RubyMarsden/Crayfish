from PyQt5.QtWidgets import QTreeWidget, QTreeWidgetItem


class SampleTreeWidget(QTreeWidget):
    def __init__(self):
        QTreeWidget.__init__(self)

        self.setHeaderLabel("Samples")

    def set_samples(self, samples):
        self.clear()
        for sample in samples:
            sample_tree_item = QTreeWidgetItem(self, [sample.name])
            sample_tree_item.sample = sample
            sample_tree_item.is_sample = True
            for spot in sample.spots:
                spot_tree_item = QTreeWidgetItem(sample_tree_item, [spot.id])
                spot_tree_item.spot = spot
                spot_tree_item.is_sample = False
