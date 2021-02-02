import copy

from PyQt5.QtCore import pyqtSignal, QObject
from models.sample import Sample
from models.spot import Spot, BACKGROUND1, BACKGROUND2
from models.york_regression import bivariate_fit
import csv
import numpy as np
import math


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
        # while in development

        equilibrium_standards = self.view.ask_user_for_equilibrium_standards(run_samples, [])
        for sample in run_samples:
            if sample in equilibrium_standards:
                sample.is_standard = True
        if equilibrium_standards is None:
            return

        age_standard_info = self.view.ask_user_for_age_standard(run_samples, equilibrium_standards)
        if age_standard_info is None:
            return

        self.manual_whole_rock_values(run_samples)
        self.view.ask_user_for_WR_activity_ratios(run_samples)

        self.standardise_all_sbm_and_calculate_time_series(run_samples)

        self.view.show_user_sbm_time_series(run_samples)

        self.normalise_all_counts_to_cps(run_samples)
        self.normalise_peak_cps_by_sbm(run_samples)
        self.calculate_outlier_resistant_mean_st_dev_for_row(run_samples)

        self.view.show_user_cps_time_series(run_samples)

        background_method = self.view.ask_user_for_background_correction_method()
        if background_method is None:
            return

        self.background_correction(run_samples, background_method)
        self.calculate_activity_ratios(run_samples)
        standard_line, standard_line_uncertainty = self.standard_line_calculation(run_samples)

        # self.view.show_user_standard_line(run_samples)

        self.age_calculation(run_samples, standard_line, standard_line_uncertainty)

        self.view.show_user_ages(run_samples)
        self.export_results(run_samples, "output")

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
                    x_list = [i for i, j in U238_232Th]
                    dx_list = [j for i, j in U238_232Th]
                    xs.extend(x_list)
                    dxs.extend(dx_list)

                    Th230_232Th = spot.data["(230Th_232Th)"]
                    y_list, dy_list = zip(*Th230_232Th)
                    ys.extend(y_list)
                    dys.extend(dy_list)

            else:
                continue
            # Fixing through the 0,0 point
            # TODO should we be fixing through the 0,0 point?
            xs.append(0), dxs.append(0.01), ys.append(0), dys.append(0.01)

        data_in_xs = np.array(xs)
        data_in_ys = np.array(ys)
        data_in_dxs = np.array(dxs)
        data_in_dys = np.array(dys)

        print(xs, dxs, ys, dys)

        a, b, S, cov_matrix = bivariate_fit(data_in_xs, data_in_ys, data_in_dxs, data_in_dys)
        print(a, b, S, cov_matrix)
        # From York 2004 - This quantity,S = SUM(Wi(Yi-bXi-a)^2, is the same one minimized in the least-squares
        # formulation of the fitting problem.4 If n points are being fitted, the expected value of S has a x^2
        # distribution for n-2 degrees of freedom, so that the expected value of S/(n-2) is unity.
        print(S / (len(xs) - 2))

        standard_line = b
        standard_line_uncertainty = math.sqrt(cov_matrix[0][0])
        return standard_line, standard_line_uncertainty

    def age_calculation(self, samples, standard_line, standard_line_uncertainty):
        for sample in samples:
            if sample.is_standard:
                continue
            for spot in sample.spots:
                spot.age_calculation(
                    sample.WR_activity_ratio,
                    sample.WR_activity_ratio_uncertainty,
                    standard_line,
                    standard_line_uncertainty
                )
                spot.calculate_error_weighted_mean_and_st_dev_for_ages()

    def manual_whole_rock_values(self, samples):
        for sample in samples:
            if sample.name == "545":
                sample.WR_activity_ratio = 0.584
                sample.WR_activity_ratio_uncertainty = 0.065
            elif sample.name == "428":
                sample.WR_activity_ratio = 0.404
                sample.WR_activity_ratio_uncertainty = 0.035
            elif sample.name == "566":
                sample.WR_activity_ratio = 0.414
                sample.WR_activity_ratio_uncertainty = 0.018
            elif sample.name == "366":
                sample.WR_activity_ratio = 0.709
                sample.WR_activity_ratio_uncertainty = 0.069
            elif sample.name == "812":
                sample.WR_activity_ratio = 0.681
                sample.WR_activity_ratio_uncertainty = 0.080
            else:
                sample.WR_activity_ratio = None
                sample.WR_activity_ratio_uncertainty = None

    ################
    ## Exporting ###
    ################

    def export_results(self, samples, filename):
        with open(filename + '.csv', 'w', newline='') as csvfile:
            writer = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
            writer.writerow(["sample name", "WR", "uncertainty", "age", "uncertainty"])
            for sample in samples:
                if sample.is_standard:
                    continue
                for spot in sample.spots:
                    row = [spot.name,
                           sample.WR_activity_ratio,
                           sample.WR_activity_ratio_uncertainty,
                           spot.data["weighted age"][0],
                           spot.data["weighted age"][1]
                           ]
                    row = [str(r) for r in row]
                    writer.writerow(row)


class Signals(QObject):
    sample_list_updated = pyqtSignal([list, list])
