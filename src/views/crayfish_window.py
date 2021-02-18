from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import QMainWindow, QLabel, QGridLayout, QWidget, QDialog, QMessageBox, QInputDialog
from PyQt5.QtCore import QSize

from views.results_dialog import ResultsDialog
from views.samples_overview import SamplesOverview
from views.standard_selection_dialog import EquilibriumStandardSelectionDialog, AgeStandardSelectionDialog
from views.whole_rock_activity_input_dialog import WholeRockActivityDialog


class CrayfishWindow(QMainWindow):
    def __init__(self, model):
        QMainWindow.__init__(self)

        self.setMinimumSize(QSize(640, 480))
        self.setWindowTitle("Crayfish - v0.0")

        samples_overview = SamplesOverview(model)
        self.setCentralWidget(samples_overview)

    def ask_user_for_equilibrium_standards(self, samples, unavailable_samples):
        dialog = EquilibriumStandardSelectionDialog(samples, unavailable_samples)
        result = dialog.exec()
        if result == QDialog.Accepted:
            return dialog.get_selected_samples()
        return None

    def ask_user_for_age_standard(self, samples, unavailable_samples):
        reply = QMessageBox.question(self, "Age standard", "Do you have an age standard?", QMessageBox.Yes,
                                     QMessageBox.No)
        if reply == QMessageBox.No:
            return False, None, None

        dialog = AgeStandardSelectionDialog(samples, unavailable_samples)
        result = dialog.exec()
        if result == QDialog.Rejected:
            return None

        sample = dialog.get_selected_samples()[0]
        # TODO make this input dialog the correct size
        age, ok_pressed = QInputDialog.getDouble(self, "Age standard",
                                                 "What is the age of sample " + sample.name + " (ka)?",
                                                 0, 0, 500)

        if not ok_pressed:
            return None

        return True, sample, age

    def ask_user_for_WR_activity_ratios(self, samples):
        dialog = WholeRockActivityDialog(samples)
        result = dialog.exec()

    def show_user_results(self, samples, default_config, ensure_config_calculated_callback, model_data, export_data_callback):
        dialog = ResultsDialog(samples, default_config, ensure_config_calculated_callback, model_data, export_data_callback)
        result = dialog.exec()
