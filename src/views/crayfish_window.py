from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import QMainWindow, QLabel, QGridLayout, QWidget, QDialog
from PyQt5.QtCore import QSize

from views.samples_overview import SamplesOverview
from views.standard_selection_dialog import StandardSelectionDialog


class CrayfishWindow(QMainWindow):
    def __init__(self, model):
        QMainWindow.__init__(self)

        self.setMinimumSize(QSize(640, 480))
        self.setWindowTitle("Crayfish - v0.0")

        samples_overview = SamplesOverview(model)
        self.setCentralWidget(samples_overview)

    def ask_user_for_standards(self, samples):
        dialog = StandardSelectionDialog(samples)
        result = dialog.exec()
        return result == QDialog.Accepted
