import copy

from PyQt5.QtCore import pyqtSignal, QObject
from models.sample import Sample
from models.spot import Spot
import csv


class CrayfishModel():
    def __init__(self):
        self.samples_by_name = {}
        self.imported_files = []
        self.signals = Signals()
        self.view = None

    def set_view(self, view):
        self.view = view

    ###############
    ## Importing ##
    ###############

    def import_samples(self, file_name, replace):
        if replace:
            self.samples_by_name = {}
            self.imported_files = []

        if file_name in self.imported_files:
            raise Exception("This file has already been imported")

        spots = self._parse_csv_file_into_spots(file_name)

        self._add_samples_from_spots(spots)
        self.imported_files.append(file_name)

        samples = list(self.samples_by_name.values())
        self.signals.sample_list_updated.emit(samples, self.imported_files)

    def _parse_csv_file_into_spots(self, file_name):
        # import csv of pd data
        with open(file_name, newline='') as csvfile:
            csv_string_data = list(csv.reader(csvfile))

        # finding the first spot
        current_line_number = 0;
        while csv_string_data[current_line_number][0] != "***":
            current_line_number += 1
        current_line_number += 1

        # making a list of spots (it's empty now)
        spots = []
        spot_data = []
        while current_line_number < len(csv_string_data):
            while current_line_number < len(csv_string_data) and csv_string_data[current_line_number][0] != "***":
                spot_data.append(csv_string_data[current_line_number])
                current_line_number = current_line_number + 1
            spot = Spot(spot_data)
            spots.append(spot)
            spot_data = []
            current_line_number += 1
        return spots

    def _add_samples_from_spots(self, spots):
        for spot in spots:
            if spot.sample_name not in self.samples_by_name:
                self.samples_by_name[spot.sample_name] = Sample(spot.sample_name)
            self.samples_by_name[spot.sample_name].spots.append(spot)

    ################
    ## Processing ##
    ################
    def process_samples(self):
        run_samples = copy.deepcopy(list(self.samples_by_name.values()))
        self.view.ask_user_for_standards(run_samples)




class Signals(QObject):
    # Define a new signal called 'trigger' that has no arguments.
    sample_list_updated = pyqtSignal([list, list])