import sys

from PyQt5.QtWidgets import QMessageBox, QApplication

from models.crayfish_model import CrayfishModel
from views.crayfish_window import CrayfishWindow


def set_except_hook(window):
    def except_hook(cls, exception, traceback):
        sys.__excepthook__(cls, exception, traceback)
        QMessageBox.critical(window, "Error", str(exception))

    sys.excepthook = except_hook


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    model = CrayfishModel()
    window = CrayfishWindow(model)
    model.set_view(window)

    set_except_hook(window)
    # model.import_samples("C:/Users/19402828/Documents/Python Scripts/Crayfish\data/k7.pd")
    window.show()
    sys.exit(app.exec_())
