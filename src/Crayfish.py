import sys

from PyQt5.QtWidgets import QMessageBox
from qtpy import QtWidgets

from models.crayfish_model import CrayfishModel
from views.crayfish_window import CrayfishWindow

def set_except_hook(window):
    def except_hook(cls, exception, traceback):
        sys.__excepthook__(cls, exception, traceback)
        QMessageBox.critical(window,"Error", str(exception))
    sys.excepthook = except_hook

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    app.setStyle("Fusion")
    model = CrayfishModel()
    window = CrayfishWindow(model)
    set_except_hook(window)
    window.show()
    sys.exit(app.exec_())
