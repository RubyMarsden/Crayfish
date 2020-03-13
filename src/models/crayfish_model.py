from PyQt5.QtCore import pyqtSignal, QObject
from models.sample import Sample
from models.spot import FakeSpot


class CrayfishModel():
    def __init__(self):
        self.samples = []
        self.signals = Signals()

    def import_samples(self, filename, replace):
        sample1 = Sample("sample1")
        sample2 = Sample("sample2")
        imported_samples = [sample1, sample2]
        spot1 = FakeSpot("spot1")
        spot2 = FakeSpot("spot2")
        spot3 = FakeSpot("spot3")
        sample1.spots = [spot1, spot2]
        sample2.spots = [spot3]

        if replace:
            self.samples = imported_samples
        else:
            self.samples.extend(imported_samples)

        self.signals.sample_list_updated.emit(self.samples)


class Signals(QObject):
    # Define a new signal called 'trigger' that has no arguments.
    sample_list_updated = pyqtSignal(list)