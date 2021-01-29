import copy

from PyQt5.QtCore import pyqtSignal, QObject
from models.sample import Sample
from models.spot import Spot, BACKGROUND1, BACKGROUND2
from models.york_regression import bivariate_fit
import csv
import numpy as np


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

        self.standardise_all_sbm_and_calculate_time_series(run_samples)

        self.normalise_all_counts_to_cps(run_samples)
        self.normalise_peak_cps_by_sbm(run_samples)
        self.calculate_outlier_resistant_mean_st_dev_for_row(run_samples)

        equilibrium_standards = self.view.ask_user_for_equilibrium_standards(run_samples, [])
        for sample in run_samples:
            if sample in equilibrium_standards:
                sample.is_standard = True
        if equilibrium_standards is None:
            return

        age_standard_info = self.view.ask_user_for_age_standard(run_samples, equilibrium_standards)
        if age_standard_info is None:
            return

        background_method = self.view.ask_user_for_background_correction_method()
        if background_method is None:
            return

        self.background_correction(run_samples, background_method)
        self.calculate_activity_ratios(run_samples)
        self.standard_line_calculation(run_samples)

        #self.age_calculation(run_samples)
        # TODO age calculation

        # THIS IS ONLY HERE FOR DEVELOPMENT
        self.view.show_user_sbm_time_series(run_samples)
        self.view.show_user_cps_time_series(run_samples)
        self.view.show_user_ages(run_samples)

    def standardise_all_sbm_and_calculate_time_series(self, samples):
        for sample in samples:
            for spot in sample.spots:
                spot.standardise_sbm_and_subtract_sbm_background()
                spot.calculate_sbm_time_series()

    def normalise_all_counts_to_cps(self, samples):
        for sample in samples:
            for spot in sample.spots:
                spot.normalise_all_counts_to_cps()

    def normalise_peak_cps_by_sbm(self, samples):
        for sample in samples:
            for spot in sample.spots:
                spot.normalise_peak_cps_by_sbm()

    def calculate_outlier_resistant_mean_st_dev_for_row(self, samples):
        for sample in samples:
            for spot in sample.spots:
                spot.calculate_outlier_resistant_mean_st_dev_for_rows()

    def background_correction(self, samples, background_method: str):
        for sample in samples:
            for spot in sample.spots:
                spot.background_correction(background_method, spot.massPeaks[BACKGROUND1], spot.massPeaks[BACKGROUND2])

    def calculate_activity_ratios(self, samples):
        for sample in samples:
            for spot in sample.spots:
                spot.calculate_activity_ratios()

    def standard_line_calculation(self, samples):
        xs = []
        ys = []
        dxs = []
        dys = []
        for sample in samples:
            if sample.is_standard:
                print(sample.name)
                for spot in sample.spots:
                    U238_232Th = spot.data["(238U_232Th)"]
                    x_list = [i for i,j in U238_232Th]
                    dx_list = [j for i,j in U238_232Th]
                    xs.extend(x_list)
                    dxs.extend(dx_list)

                    Th230_232Th = spot.data["(230Th_232Th)"]
                    y_list, dy_list = zip(*Th230_232Th)
                    ys.extend(y_list)
                    dys.extend(dy_list)

            else:
                continue

        data_in_xs = np.array(xs)
        data_in_ys = np.array(ys)
        data_in_dxs = np.array(dxs)
        data_in_dys = np.array(dys)

        print(xs, dxs, ys, dys)

        a, b, S, cov_matrix = bivariate_fit(data_in_xs, data_in_ys, data_in_dxs, data_in_dys)
        print(a, b, S, cov_matrix)
        return

    """
    def age_calculation(self, samples):
        for sample in samples:
            if not sample.is_standard:
                for spot in sample.spots:
                    spot.age_calculation()
    """

class Signals(QObject):
    sample_list_updated = pyqtSignal([list, list])
