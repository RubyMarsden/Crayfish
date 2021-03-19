import copy

from PyQt5.QtCore import pyqtSignal, QObject

from models.background_method import BackgroundCorrection
from models.configuration import Configuration
from models.data_key import DataKey
from models.mathbot import calculate_error_weighted_mean_and_st_dev
from models.sample import Sample
from models.settings import NONBACKGROUND
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
        self.data = {}
        self.configurations_calculated = set()

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

        spots = self._parse_pd_file_into_spots(file_name)

        self._add_samples_from_spots(spots)
        self.imported_files.append(file_name)

        samples = list(self.samples_by_name.values())
        self.signals.sample_list_updated.emit(samples, self.imported_files)

    def _parse_pd_file_into_spots(self, filename):
        file = open(filename, "rt")
        pd_file_data = file.readlines()
        pd_data = []
        for line in pd_file_data:
            # line is a string
            # Make line split into words - by using comma and spaces together - make into list of lists
            line_list = [word.replace(",", "") for word in line.split()]
            pd_data.append(line_list)

        # finding the first spot
        current_line_number = 0;
        while pd_data[current_line_number] != ["***"]:
            current_line_number += 1
        current_line_number += 1

        # making a list of spots (it's empty now)
        spots = []
        spot_data = []
        while current_line_number < len(pd_data):
            while current_line_number < len(pd_data) and pd_data[current_line_number] != ["***"]:
                spot_data.append(pd_data[current_line_number])
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
        self.clear_previous_calculations()

        samples = list(self.samples_by_name.values())
        equilibrium_standards = self.view.ask_user_for_equilibrium_standards(samples, [])
        if equilibrium_standards is None:
            return
        for sample in samples:
            if sample in equilibrium_standards:
                sample.is_standard = True

        age_standard_info = self.view.ask_user_for_age_standard(samples, equilibrium_standards)
        if age_standard_info is None:
            return

        self.manual_whole_rock_values(samples)
        self.view.ask_user_for_WR_activity_ratios(samples)

        self.standardise_all_sbm_and_calculate_time_series(samples)

        default_config = Configuration(
            normalise_by_sbm=True,
            background_method=BackgroundCorrection.EXP,
            excluded_spots=frozenset()
        )

        self.view.show_user_results(samples, default_config, self.ensure_config_calculated, self.data, self.export_results)

        # self.export_test_csv(config, samples)

    def clear_previous_calculations(self):
        self.data.clear()
        self.configurations_calculated.clear()
        for sample in self.samples_by_name.values():
            for spot in sample.spots:
                spot.clear_previous_calculations()

    def setup_new_config_calculation(self, config):
        self.data[config] = {}
        self.configurations_calculated.add(config)
        for sample in self.samples_by_name.values():
            for spot in sample.spots:
                spot.setup_new_config_calculation(config)

    def ensure_config_calculated(self, config):
        if config not in self.configurations_calculated:
            self.calculate_for_config(config)

    def calculate_for_config(self, config):
        self.setup_new_config_calculation(config)
        samples = self.samples_by_name.values()
        self.normalise_all_counts_to_cps(config, samples)
        self.calculate_outlier_resistant_mean_st_dev_for_row(config, samples)
        self.get_U_mean(config, samples)
        # TODO
        # self.get_limit_detection_difference(config, samples)
        self.background_correction(config, samples)
        self.calculate_activity_ratios(config, samples)
        self.standard_line_calculation(config, samples)
        self.calculate_ages_and_weighted_mean_age(config, samples)

    def standardise_all_sbm_and_calculate_time_series(self, samples):
        for sample in samples:
            for spot in sample.spots:
                spot.standardise_sbm_and_subtract_sbm_background()
                spot.calculate_sbm_time_series()

    def normalise_all_counts_to_cps(self, config, samples):
        for sample in samples:
            for spot in sample.spots:
                spot.normalise_all_counts_to_cps(config)

    def calculate_outlier_resistant_mean_st_dev_for_row(self, config, samples):
        for sample in samples:
            for spot in sample.spots:
                spot.calculate_outlier_resistant_mean_st_dev_for_rows(config)

    def background_correction(self, config, samples):
        for sample in samples:
            for spot in sample.spots:
                spot.background_correction(config, spot.massPeaks[BACKGROUND1], spot.massPeaks[BACKGROUND2])

    def calculate_activity_ratios(self, config, samples):
        for sample in samples:
            for spot in sample.spots:
                if spot in config.excluded_spots:
                    spot.data[config][DataKey.ACTIVITY_RATIOS] = "Excluded spot"
                else:
                    spot.calculate_activity_ratios(config)

    def standard_line_calculation(self, config, samples):
        xs = []
        ys = []
        dxs = []
        dys = []
        for sample in samples:
            if not sample.is_standard:
                continue

            for spot in sample.spots:
                if spot in config.excluded_spots:
                    spot.data[config][DataKey.WEIGHTED_ACTIVITY_RATIO] = "Spot not included"
                    continue

                activity_ratios = spot.data[config][DataKey.ACTIVITY_RATIOS]
                spot_xs = []
                spot_ys = []
                spot_dxs = []
                spot_dys = []
                for ratio in activity_ratios:
                    if isinstance(ratio, str):
                        continue
                    (x, dx), (y, dy) = ratio
                    spot_xs.append(x)
                    spot_dxs.append(dx)
                    spot_ys.append(y)
                    spot_dys.append(dy)

                xs.extend(spot_xs)
                dxs.extend(spot_dxs)
                ys.extend(spot_ys)
                dys.extend(spot_dys)

        # Fixing through the 0,0 point
        xs.append(0), dxs.append(0.00001), ys.append(0), dys.append(0.00001)

        data_in_xs = np.array(xs)
        data_in_ys = np.array(ys)
        data_in_dxs = np.array(dxs)
        data_in_dys = np.array(dys)

        a, b, S, cov_matrix = bivariate_fit(data_in_xs, data_in_ys, data_in_dxs, data_in_dys)

        # From York 2004 - This quantity,S = SUM(Wi(Yi-bXi-a)^2, is the same one minimized in the least-squares
        # formulation of the fitting problem. If n points are being fitted, the expected value of S has a x^2
        # distribution for n-2 degrees of freedom, so that the expected value of S/(n-2) is unity. Here - as we've taken
        # away a degree of freedom by fixing through x, y = 0, 0 S/(n-3) is used instead.
        MSWD = S / (len(xs) - 3)
        standard_line_uncertainty = math.sqrt(cov_matrix[0][0])

        self.data[config][DataKey.STANDARD_LINE_GRADIENT] = b, standard_line_uncertainty
        self.data[config][DataKey.STANDARD_LINE_MSWD] = MSWD

    def calculate_ages_and_weighted_mean_age(self, config, samples):
        gradient, gradient_uncertainty = self.data[config][DataKey.STANDARD_LINE_GRADIENT]
        for sample in samples:
            if sample.is_standard:
                continue
            for spot in sample.spots:
                if spot in config.excluded_spots:
                    spot.data[config][DataKey.AGES] = "Spot is excluded"
                    spot.data[config][DataKey.WEIGHTED_AGE] = ("Error! No ages to take weighted mean from.", "")

                else:
                    spot.calculate_age_per_scan(
                        config,
                        sample.WR_activity_ratio,
                        sample.WR_activity_ratio_uncertainty,
                        gradient,
                        gradient_uncertainty
                    )
                    spot.calculate_error_weighted_mean_and_st_dev_for_ages(config)

    def get_U_mean(self, config, samples):
        for sample in samples:
            for spot in sample.spots:
                if spot in config.excluded_spots:
                    spot.data[config][DataKey.U_CONCENTRATION] = "Excluded spot"
                    continue
                spot.calculate_error_weighted_mean_and_st_dev_U_cps(config)

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

    def export_results(self, config, samples, filename):
        non_standard_samples = [sample for sample in samples if not sample.is_standard]
        headers = self.get_export_headers(non_standard_samples)
        with open(filename + " " + str(config) + '.csv', 'w', newline='') as csvfile:
            writer = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
            writer.writerow(headers)
            for sample in non_standard_samples:
                for spot in sample.spots:
                    scan_row = []
                    for result in spot.data[config][DataKey.AGES]:
                        if isinstance(result, str):
                            scan_row.append(result)
                            scan_row.append("")
                        else:
                            age, uncertainty = result
                            scan_row.append(age)
                            scan_row.append(uncertainty)

                    fixed_row = [spot.name,
                                 sample.WR_activity_ratio,
                                 sample.WR_activity_ratio_uncertainty,
                                 self.data[config][DataKey.STANDARD_LINE_GRADIENT][0],
                                 self.data[config][DataKey.STANDARD_LINE_GRADIENT][1],
                                 self.data[config][DataKey.STANDARD_LINE_MSWD],
                                 spot.data[config][DataKey.WEIGHTED_AGE][0],
                                 spot.data[config][DataKey.WEIGHTED_AGE][1],
                                 spot.data[config][DataKey.U_CONCENTRATION][0],
                                 spot.data[config][DataKey.U_CONCENTRATION][1]
                                 ]
                    write_row = fixed_row + scan_row
                    write_row = [str(r) for r in write_row]
                    writer.writerow(write_row)

    def get_export_headers(self, samples):
        fixed_headers = [
            "sample-spot name",
            "WR",
            "uncertainty",
            "standard line gradient",
            "uncertainty",
            "MSWD",
            "weighted age",
            "uncertainty",
            "Weighted U cps",
            "uncertainty"
        ]
        max_number_of_scans = max([spot.numberOfScans for sample in samples for spot in sample.spots])
        scan_headers = []
        for i in range(max_number_of_scans):
            scan_header = f"Scan {i +1}"
            uncertainty_header = f"Scan {i + 1} uncertainty"
            scan_headers.append(scan_header)
            scan_headers.append(uncertainty_header)

        return fixed_headers + scan_headers

    def export_test_csv(self, config, samples):
        test_sample = [sample for sample in samples if sample.name == "test"]
        headers = []

        with open(f"test output {config}" + '.csv', 'w', newline='') as csvfile:
            writer = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
            writer.writerow(headers)
            for sample in test_sample:
                for spot in sample.spots:
                    activity_row = []
                    for value, uncertainty in spot.data[config][DataKey.ACTIVITY_RATIOS]:
                        activity_row.append(value)
                        activity_row.append(uncertainty)
                    for mp in spot.massPeaks.values():
                        for row in mp.rows:
                            fixed_row = [spot.name, mp.name]
                            cps_row = []
                            for i in row.data[config][DataKey.CPS]:
                                cps_row.append(i)

                            outlier_res_mean, outlier_res_stdev = row.data[config][DataKey.OUTLIER_RES_MEAN_STDEV]
                            if mp.name in NONBACKGROUND:
                                background_corr, stdev = row.data[config][DataKey.BKGRD_CORRECTED]
                            else:
                                background_corr, stdev = None, None

                            data_row = [outlier_res_mean, outlier_res_stdev, background_corr, stdev]

                            write_row = fixed_row + cps_row + data_row + activity_row

                            write_row = [str(r) for r in write_row]
                            writer.writerow(write_row)


class Signals(QObject):
    sample_list_updated = pyqtSignal([list, list])

