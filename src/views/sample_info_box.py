from PyQt5.QtWidgets import QGroupBox


class SampleInfoBox(QGroupBox):
    def __init__(self):
        QGroupBox.__init__(self,'Sample')

    def display_sample(self, sample):
        self.setTitle("Sample: " + sample.name)

    def display_spot_list
        pass