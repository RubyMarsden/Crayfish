from enum import Enum

from models.background_method import BackgroundCorrection
from models.mathbot import *
from models.settings import *
import math


class DataKey(Enum):
    SBM_STANDARDISED = "sbm standardised"
    COUNTS_PER_SECOND = "counts `per second"
    SBM_NORMALISED = "cps normalised by sbm"
    OUTLIER_RES_MEAN_STDEV = "outlier resistant mean and st deviation for cps values"
    OUTLIER_RES_MEAN_STDEV_SBM = "outlier resistant mean and st deviation for sbm normalised values"
    BKGRD_CORRECTED = "background correction applied to outlier resistant mean and st deviation for cps values"
    BKGRD_CORRECTED_SBM = "background correction applied to outlier resistant mean and st deviation for sbm normalised values"


# contains the data for a single scan within a single mass peak within a spot
class Row:
    def __init__(self, spotName, mpName, scanNumber, massPeakValue, countData, sbmData):
        self.name = spotName + " " + mpName + " " + str(scanNumber)
        self.mpName = mpName
        self.scan_number = str(scanNumber)
        # self.time = timeOfScan
        self.massPeakValue = massPeakValue

        self.rawRows = {"counts": countData, "sbm": sbmData}

        self.data = {}

    def __repr__(self):
        return self.name

    def standardise_sbm_and_subtract_sbm_background(self, sbm_background, count_time):
        self.data[DataKey.SBM_STANDARDISED] = [i * MEASUREMENTS_PER_SCAN_PER_MASS_PEAK / count_time - sbm_background for
                                               i in self.rawRows["sbm"]]

    def get_local_sbm_time_series(self, count_time, start_time):
        points = self.data[DataKey.SBM_STANDARDISED]
        time_per_measurement = count_time / len(points)
        local_sbm_time_series = [start_time + (i + 0.5) * time_per_measurement for i in range(len(points))]
        return zip(local_sbm_time_series, points)

    def normalise_all_counts_to_cps(self, count_time):
        self.data[DataKey.COUNTS_PER_SECOND] = [i * MEASUREMENTS_PER_SCAN_PER_MASS_PEAK / count_time for i in
                                                self.rawRows["counts"]]

    def normalise_peak_cps_by_sbm(self):
        cps = self.data[DataKey.COUNTS_PER_SECOND]
        sbm = self.data[DataKey.SBM_STANDARDISED]
        self.data[DataKey.SBM_NORMALISED] = [i / j for i, j in zip(cps, sbm)]

    def calculate_mean_and_st_dev_blocks(self):
        self.data[DataKey.OUTLIER_RES_MEAN_STDEV] = calculate_outlier_resistant_mean_and_st_dev(
            self.data[DataKey.COUNTS_PER_SECOND], NUMBER_OF_OUTLIERS_ALLOWED)
        self.data[DataKey.OUTLIER_RES_MEAN_STDEV_SBM] = calculate_outlier_resistant_mean_and_st_dev(
            self.data[DataKey.SBM_NORMALISED], NUMBER_OF_OUTLIERS_ALLOWED)

    def background_correction_230Th(self, background_method, background1, background2):
        if background_method == BackgroundCorrection.EXP:
            self.exponential_correction(background1, background2, DataKey.BKGRD_CORRECTED,
                                        DataKey.OUTLIER_RES_MEAN_STDEV)
            self.exponential_correction(background1, background2, DataKey.BKGRD_CORRECTED_SBM,
                                        DataKey.OUTLIER_RES_MEAN_STDEV_SBM)
        elif background_method == BackgroundCorrection.LIN:
            self.linear_correction(background1, background2, DataKey.BKGRD_CORRECTED,
                                   DataKey.OUTLIER_RES_MEAN_STDEV)
            self.linear_correction(background1, background2, DataKey.BKGRD_CORRECTED_SBM,
                                   DataKey.OUTLIER_RES_MEAN_STDEV_SBM)
        elif background_method == BackgroundCorrection.CONST:
            self.constant_background_correction(background2)
        else:
            raise Exception("No background correction selected")

    def constant_background_correction(self, background2):
        keys = DataKey.OUTLIER_RES_MEAN_STDEV, DataKey.BKGRD_CORRECTED
        sbm_keys = DataKey.OUTLIER_RES_MEAN_STDEV_SBM, DataKey.BKGRD_CORRECTED_SBM

        for input_key, output_key in [keys, sbm_keys]:
            cps, uncertainty = self.data[input_key]
            cps_b2, uncertainty_b2 = background2.data[input_key]
            cps_corrected = cps - cps_b2
            cps_corrected_uncertainty = errors_in_quadrature([uncertainty, uncertainty_b2])

            self.data[output_key] = cps_corrected, cps_corrected_uncertainty

    def exponential_correction(self, background1, background2, key_output, key_input):
        if self.mpName != "ThO246":
            raise Exception("Calling exponential background subtraction on a non-ThO246 mass peak")

        cps, uncertainty = self.data[key_input]
        cps_b1, uncertainty_b1 = background1.data[key_input]
        cps_b2, uncertainty_b2 = background2.data[key_input]

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

        self.data[key_output] = background_corrected_cps, background_corrected_uncertainty
        # If the correction function needs to be plotted at any point - just in case!
        if isConstant:
            self.data["expCorrectionFunction"] = lambda x: cps_b2
        else:
            self.data["expCorrectionFunction"] = lambda x: a * math.exp(b * (x - x1))

    def linear_correction(self, background1, background2, key_output, key_input):
        if self.mpName != "ThO246":
            raise Exception("Calling linear background subtraction on a non-ThO246 mass peak")
        cps, uncertainty = self.data[key_input]
        cps_b1, uncertainty_b1 = background1.data[key_input]
        cps_b2, uncertainty_b2 = background2.data[key_input]
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

        self.data[key_output] = background_corrected_cps, background_corrected_uncertainty
        # If the correction function needs to be plotted at any point - just in case!
        if isConstant:
            self.data["linearCorrectionFunction"] = lambda x: cps_b2
        else:
            self.data["linearCorrectionFunction"] = lambda x: gradient * x + c
