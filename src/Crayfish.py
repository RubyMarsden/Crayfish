import sys

from qtpy import QtWidgets

from models.crayfish_model import CrayfishModel
from views.crayfish_window import CrayfishWindow

def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)

if __name__ == "__main__":
    sys.excepthook = except_hook
    app = QtWidgets.QApplication(sys.argv)
    app.setStyle("Fusion")
    model = CrayfishModel()
    window = CrayfishWindow(model)
    window.show()
    sys.exit(app.exec_())
