from PyQt5.QtWidgets import QGroupBox, QListWidgetItem, QListWidget, QLabel, QFormLayout


class SampleInfoBox(QGroupBox):
    def __init__(self):
        QGroupBox.__init__(self,'Sample')

        self.spot_list = QListWidget()

        layout = QFormLayout()
        layout.addRow(QLabel("Spots:"), self.spot_list)

        self.setLayout(layout)

    def display_sample(self, sample):
        self.setTitle("Sample: " + sample.name)

        self.spot_list.clear()
        for spot in sample.spots:
            spot = QListWidgetItem(spot.name, self.spot_list)
