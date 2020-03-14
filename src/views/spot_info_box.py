from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QGroupBox, QFormLayout, QLabel, QListWidget, QListWidgetItem


class SpotInfoBox(QGroupBox):
    def __init__(self):
        QGroupBox.__init__(self,'Spot')

        self.number_of_scans_label = QLabel()
        self.number_of_peaks_label = QLabel()
        self.mass_peaks_list = QListWidget()
        self.mass_peaks_list.setEnabled(False)

        layout = QFormLayout()
        layout.addRow(QLabel("Number of scans:"), self.number_of_scans_label)
        layout.addRow(QLabel("Number of peaks:"), self.number_of_peaks_label)
        layout.addRow(QLabel("Mass peaks measured:"), self.mass_peaks_list)

        self.setLayout(layout)

    def display_spot(self, spot):
        self.setTitle("Spot: " + spot.name)
        self.number_of_scans_label.setText(str(spot.numberOfScans))
        self.number_of_peaks_label.setText(str(spot.numberOfPeaks))
        self.mass_peaks_list.clear()
        for mass_peak_name in spot.mpNames:
            mass_peak_name_item = QListWidgetItem(mass_peak_name, self.mass_peaks_list)
            mass_peak_name_item.setFlags(mass_peak_name_item.flags() & ~Qt.ItemIsSelectable)
