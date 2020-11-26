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

        self.normalise_all_sbm_and_calculate_time_series(run_samples)
        # THIS IS ONLY HERE FOR DEVELOPMENT
        self.view.show_user_cps_time_series(run_samples)
        self.view.show_user_sbm_time_series(run_samples)

        equilibrium_standards = self.view.ask_user_for_equilibrium_standards(run_samples, [])
        if equilibrium_standards is None:
            return

        age_standard_info = self.view.ask_user_for_age_standard(run_samples, equilibrium_standards)
        if age_standard_info is None:
            return



        background_method = self.view.ask_user_for_background_correction_method()
        if background_method is None:
            return

    def normalise_all_sbm_and_calculate_time_series(self, samples):
        for sample in samples:
            for spot in sample.spots:
                spot.normalise_sbm_and_subtract_sbm_background()
                spot.calculate_sbm_time_series()

    def normalise_all_counts_to_cps(self, samples):
        for sample in samples:
            for spot in sample.spots:
                spot.normalise_all_counts_to_cps()

    def linear_sbm_interpolation_and_correction_by_scan(self, samples):
        for sample in samples:
            for spot in sample.spots:
                spot.normalise_counts_to_sbm()

    def outlier_resistant_mean_st_dev_for_row(self, samples):
        for sample in samples:
            for spot in sample.spots:
                spot.calculate_row_mean_st_dev()

    def background_correction(self, samples, background_method):
        pass

    def standard_line_calculation(self, samples):
        for sample in samples:
            if sample.is_standard:
                pass


class Signals(QObject):
    sample_list_updated = pyqtSignal([list, list])
