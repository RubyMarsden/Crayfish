from enum import Enum

from models.background_method import BackgroundCorrection
from models.mathbot import *
from models.settings import *
import math

class DataKey(Enum):
    SBM_STANDARDISED = "sbm standardised"
    COUNTS_PER_SECOND = "counts `per second"
    SBM_NORMALISED = "cps normalised by sbm"
    TH230_MASS_PEAK_EXP_BACKGROUND_CORRECTED = "230Th_mass_peak_exp_background_corrected"

# contains the data for a single scan within a single mass peak within a spot
class Row:
    def __init__(self, spotName, mpName, scanNumber, massPeakValue, countData, sbmData):
        self.name = spotName + " " + mpName + " " + str(scanNumber)
        self.mpName = mpName
        self.scan_number = str(scanNumber)
        # self.time = timeOfScan
        self.massPeakValue = massPeakValue

        self.rawRows = {}
        self.rawRows["counts"] = countData
        self.rawRows["sbm"] = sbmData

        self.data = {}

    def __repr__(self):
        return self.name

    def standardise_sbm_and_subtract_sbm_background(self, sbm_background, count_time):
        self.data[DataKey.SBM_STANDARDISED] = [i * MEASUREMENTS_PER_SCAN_PER_MASS_PEAK / count_time - sbm_background for i in self.rawRows["sbm"]]

    def get_local_sbm_time_series(self, count_time, start_time):
        points = self.data[DataKey.SBM_STANDARDISED]
        time_per_measurement = count_time / len(points)
        local_sbm_time_series = [start_time + (i + 0.5) * time_per_measurement for i in range(len(points))]
        return zip(local_sbm_time_series, points)

    def normalise_all_counts_to_cps(self, count_time):
        self.data[DataKey.COUNTS_PER_SECOND] = [i * MEASUREMENTS_PER_SCAN_PER_MASS_PEAK / count_time for i in self.rawRows["counts"]]

    def normalise_peak_cps_by_sbm(self):
        cps = self.data[DataKey.COUNTS_PER_SECOND]
        sbm = self.data[DataKey.SBM_STANDARDISED]
        self.data[DataKey.SBM_NORMALISED] = [i / j for i, j in zip(cps, sbm)]

    def calculate_mean_and_st_dev_blocks(self, input_key, output_key):
        self.data[output_key] = calculateOutlierResistantMeanAndStDev(self.data[input_key], NUMBER_OF_OUTLIERS_ALLOWED)

    def background_correction_230Th(self, background_method, background1, background2):
        if background_method == BackgroundCorrection.EXP:
            self.exponential_correction(background1, background2, DataKey.TH230_MASS_PEAK_EXP_BACGROUND_CORRECTED, DataKey.COUNTS_PER_SECOND)
            self.exponential_correction(background1, background2, "ThO246 exp corrected sbm normalised",
                                        DataKey.SBM_NORMALISED)
        elif background_method == BackgroundCorrection.LIN:
            self.linear_correction(background1, background2)
        elif background_method == BackgroundCorrection.CONST:
            self.constant_correction(background2)
        else:
            raise Exception("No background correction selected")

    def background_correction_all_peaks(self, background2):
        # if self.mpName not in mpNamesNonBackground:
        # raise Exception("Calling background subtraction on a background peak")
        cps = self.data[DataKey.COUNTS_PER_SECOND]
        cps_sbm = self.data[DataKey.SBM_NORMALISED]

        bckgrd_cps = background2.data[DataKey.COUNTS_PER_SECOND]
        bckgrd_cps_sbm = background2.data[DataKey.SBM_NORMALISED]

        self.data["background corrected all peaks"] = [i-j for i, j in zip(cps, bckgrd_cps)]
        self.data["sbm normalised background corrected all peaks"] = [i-j for i, j in zip(cps_sbm, bckgrd_cps_sbm)]

    def exponential_correction(self, background1, background2, key_output, key_input):
        if self.mpName != "ThO246":
            raise Exception("Calling exponential background subtraction on a non-ThO246 mass peak")

        self.data[key_output] = []
        cps = self.data[key_input]
        bckgrd1_cps = background1.data[key_input]
        bckgrd2_cps = background2.data[key_input]

        x1 = background1.massPeakValue
        x2 = background2.massPeakValue
        xThO246 = self.massPeakValue

        for yThO246, y1, y2 in zip(cps, bckgrd1_cps, bckgrd2_cps):

            isConstant = y2 >= y1
            if isConstant:
                yEstimatedBackground = y2

            else:
                # NOTE we shift the exponential curve to x1=0 to avoid "a" becoming too large
                xThO246_shifted = xThO246 - x1
                a, b, yEstimatedBackground = estimateExponential((0, y1), (x2 - x1, y2), xThO246_shifted)
            correctedBackgroundExponentialThO246 = yThO246 - yEstimatedBackground

            self.data[key_output].append(correctedBackgroundExponentialThO246)

            if isConstant:
                self.data["expCorrectionFunction"] = lambda x: y2
            else:
                self.data["expCorrectionFunction"] = lambda x: a * math.exp(b * (x - x1))

    def linear_correction(self, background1, background2, key_output, key_input):
        if self.mpName != "ThO246":
            raise Exception("Calling linear background subtraction on a non-ThO246 mass peak")
        self.data[key_output] = []
        cps = self.data[key_input]
        bckgrd1_cps = background1.data[key_input]
        bckgrd2_cps = background2.data[key_input]
        x1 = background1.massPeakValue
        x2 = background2.massPeakValue
        xThO246 = self.massPeakValue

        for i, j, k in zip(cps, bckgrd1_cps, bckgrd2_cps):
            y1 = j
            y2 = k
            yThO246 = i

            isConstant = y2 >= y1
            if isConstant:
                yEstimatedBackground = y2
            else:
                gradient = (y2 - y1) / (x2 - x1)
                c = y1 - gradient * x1
                yEstimatedBackground = gradient * xThO246 + c

            correctedBackgroundLinearThO246 = yThO246 - yEstimatedBackground
            self.data[key_output].append(correctedBackgroundLinearThO246)

            if isConstant:
                self.data["linearCorrectionFunction"] = lambda x: y2
            else:
                self.data["linearCorrectionFunction"] = lambda x: gradient * x + c

    def constant_correction(self, background2, key_output, key_input):
        if self.mpName != "ThO246":
            raise Exception("Calling constant background subtraction on a non-ThO246 mass peak")
        self.data[key_output] = []
        cps = self.data[key_input]
        bckgrd2_cps = background2.data[key_input]

        for i, j in zip(cps, bckgrd2_cps):
            y2 = j
            yThO246 = i

            correctedBackgroundLinearThO246 = yThO246 - y2
            self.data[key_output].append(correctedBackgroundLinearThO246)
            self.data["constantCorrectionFunction"] = lambda x: y2

    ###################
    ### Not used yet###
    ###################



    def calculate_cps_mean_and_st_dev(self, countTime, inputKey, outputKey):
        mean, stDev = self.data[inputKey]
        cpsMean = mean * MEASUREMENTS_PER_SCAN_PER_MASS_PEAK / countTime
        cpsStDev = stDev * MEASUREMENTS_PER_SCAN_PER_MASS_PEAK / countTime
        self.data[outputKey] = cpsMean, cpsStDev
