from collections import defaultdict

from models.background_method import BackgroundCorrection
from models.data_key import DataKey
from models.mathbot import *
from models.settings import *
import math


# contains the data for a single scan within a single mass peak within a spot
class Row:
    def __init__(self, spotName, mpName, scanNumber, massPeakValue, countData, sbmData):
        self.name = spotName + " " + mpName + " " + str(scanNumber)
        self.mpName = mpName
        self.scan_number = str(scanNumber)
        # self.time = timeOfScan
        self.massPeakValue = massPeakValue

        self.rawRows = {DataKey.COUNTS: countData, DataKey.SBM_COUNTS: sbmData}

        self.data = {}

    def setup_new_calculation(self, configurations):
        self.data = {}
        for config in configurations:
            self.data[config] = {}

    def __repr__(self):
        return self.name

    def standardise_sbm_and_subtract_sbm_background(self, sbm_background, count_time):
        self.data[DataKey.SBM_CPS_STANDARDISED] = [i * MEASUREMENTS_PER_SCAN_PER_MASS_PEAK / count_time - sbm_background for
                                                   i in self.rawRows[DataKey.SBM_COUNTS]]

    def get_local_sbm_time_series(self, count_time, start_time):
        points = self.data[DataKey.SBM_CPS_STANDARDISED]
        time_per_measurement = count_time / len(points)
        local_sbm_time_series = [start_time + (i + 0.5) * time_per_measurement for i in range(len(points))]
        return zip(local_sbm_time_series, points)

    def normalise_all_counts_to_cps(self, config, count_time):
        cps = [i * MEASUREMENTS_PER_SCAN_PER_MASS_PEAK / count_time for i in
                                  self.rawRows[DataKey.COUNTS]]
        if config.normalise_by_sbm:
            sbm = self.data[DataKey.SBM_CPS_STANDARDISED]
            self.data[config][DataKey.CPS] = [i / j for i, j in zip(cps, sbm)]
        else:
            self.data[config][DataKey.CPS] = cps

    def calculate_mean_and_st_dev_blocks(self, config):
        self.data[config][DataKey.OUTLIER_RES_MEAN_STDEV] = calculate_outlier_resistant_mean_and_st_dev(
            self.data[config][DataKey.CPS], NUMBER_OF_OUTLIERS_ALLOWED)

    def background_correction_230Th(self, config, background_method, background1, background2):
        if background_method == BackgroundCorrection.EXP:
            self.exponential_correction(config, background1, background2)
        elif background_method == BackgroundCorrection.LIN:
            self.linear_correction(config, background1, background2)
        elif background_method == BackgroundCorrection.CONST:
            self.constant_background_correction(config, background2)
        else:
            raise Exception("No background correction selected")

    def constant_background_correction(self, config, background2):
        cps, uncertainty = self.data[config][DataKey.OUTLIER_RES_MEAN_STDEV]
        cps_b2, uncertainty_b2 = background2.data[config][DataKey.OUTLIER_RES_MEAN_STDEV]
        cps_corrected = cps - cps_b2
        cps_corrected_uncertainty = errors_in_quadrature([uncertainty, uncertainty_b2])

        self.data[config][DataKey.BKGRD_CORRECTED] = cps_corrected, cps_corrected_uncertainty

    def exponential_correction(self, config, background1, background2):
        if self.mpName != "ThO246":
            raise Exception("Calling exponential background subtraction on a non-ThO246 mass peak")

        cps, uncertainty = self.data[config][DataKey.OUTLIER_RES_MEAN_STDEV]
        cps_b1, uncertainty_b1 = background1.data[config][DataKey.OUTLIER_RES_MEAN_STDEV]
        cps_b2, uncertainty_b2 = background2.data[config][DataKey.OUTLIER_RES_MEAN_STDEV]

        x1 = background1.massPeakValue
        x2 = background2.massPeakValue
        xThO246 = self.massPeakValue

        isConstant = cps_b2 >= cps_b1
        if isConstant:
            background_corrected_cps = cps - cps_b2
            background_corrected_uncertainty = errors_in_quadrature([uncertainty, uncertainty_b2])

        else:
            # NOTE we shift the exponential curve to x1=0 to avoid "a" becoming too large
            xThO246_shifted = xThO246 - x1
            a, b, y_estimated_background, y_estimated_background_uncertainty = interpolate_to_exponential(
                point1=(0, cps_b1),
                error1=uncertainty_b1,
                point2=(x2 - x1, cps_b2),
                error2=uncertainty_b2,
                x=xThO246_shifted
            )
            background_corrected_cps = cps - y_estimated_background
            background_corrected_uncertainty = errors_in_quadrature([uncertainty, y_estimated_background_uncertainty])

        self.data[config][DataKey.BKGRD_CORRECTED] = background_corrected_cps, background_corrected_uncertainty

    def linear_correction(self, config, background1, background2):
        if self.mpName != "ThO246":
            raise Exception("Calling linear background subtraction on a non-ThO246 mass peak")
        cps, uncertainty = self.data[config][DataKey.OUTLIER_RES_MEAN_STDEV]
        cps_b1, uncertainty_b1 = background1.data[config][DataKey.OUTLIER_RES_MEAN_STDEV]
        cps_b2, uncertainty_b2 = background2.data[config][DataKey.OUTLIER_RES_MEAN_STDEV]
        x1 = background1.massPeakValue
        x2 = background2.massPeakValue
        xThO246 = self.massPeakValue

        isConstant = cps_b2 >= cps_b1
        if isConstant:
            background_corrected_cps = cps - cps_b2
            background_corrected_uncertainty = errors_in_quadrature([uncertainty, uncertainty_b2])
        else:
            gradient = (cps_b2 - cps_b1) / (x2 - x1)
            c = cps_b1 - gradient * x1
            y_estimated_background = gradient * xThO246 + c
            y_estimated_background_uncertainty = math.sqrt((((x2 - xThO246) / (x2 - x1)) * uncertainty_b1) ** 2 + (
                        ((xThO246 - x1) / (x2 - x1)) * uncertainty_b2) ** 2)

            background_corrected_cps = cps - y_estimated_background
            background_corrected_uncertainty = errors_in_quadrature([uncertainty, y_estimated_background_uncertainty])

        self.data[config][DataKey.BKGRD_CORRECTED] = background_corrected_cps, background_corrected_uncertainty
