from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import QMainWindow, QLabel, QGridLayout, QWidget
from PyQt5.QtCore import QSize

from views.samples_overview import SamplesOverview


class CrayfishWindow(QMainWindow):
    def __init__(self, model):
        QMainWindow.__init__(self)

        self.setMinimumSize(QSize(640, 480))
        self.setWindowTitle("Crayfish - v0.0")

        samples_overview = SamplesOverview(model)
        self.setCentralWidget(samples_overview)

        # centralWidget = QWidget(self)
        # self.setCentralWidget(centralWidget)
        #
        # gridLayout = QGridLayout(self)
        # centralWidget.setLayout(gridLayout)
        #
        # title = QLabel("ZirconFtWindow")
        # title.setAlignment(QtCore.Qt.AlignCenter)
        # author = QLabel("DaggittAndMarsden")
        # author.setAlignment(QtCore.Qt.AlignLeft)
        # gridLayout.addWidget(title, 0, 0)
        # gridLayout.addWidget(author,1,0)