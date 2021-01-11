from models.background_method import BackgroundCorrection
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

        self.rawRows = {}
        self.rawRows["counts"] = countData
        self.rawRows["sbm"] = sbmData

        self.data = {}

    def __repr__(self):
        return self.name

    def normalise_sbm_and_subtract_sbm_background(self, sbm_background, count_time):
        self.data["sbm_normalised"] = []
        for i in self.rawRows["sbm"]:
            i2 = i * MEASUREMENTS_PER_SCAN_PER_MASS_PEAK / count_time - sbm_background
            self.data["sbm_normalised"].append(i2)

    def get_local_sbm_time_series(self, count_time, start_time):
        points = self.data["sbm_normalised"]
        time_per_measurement = count_time / len(points)
        local_sbm_time_series = [start_time + (i + 0.5) * time_per_measurement for i in range(len(points))]
        return zip(local_sbm_time_series, points)

    def normalise_all_counts_to_cps(self, count_time):
        self.data["counts normalised to time"] = []
        for i in self.rawRows["counts"]:
            i2 = i * MEASUREMENTS_PER_SCAN_PER_MASS_PEAK / count_time
            self.data["counts normalised to time"].append(i2)

    def normalise_peak_cps_by_sbm(self):
        self.data["peak cps normalised by sbm"] = []
        cps = self.data["counts normalised to time"]
        sbm = self.data["sbm_normalised"]
        for i, j in zip(cps, sbm):
            i2 = i / j
            self.data["peak cps normalised by sbm"].append(i2)

    def background_correction_230Th(self, background_method, background1, background2):
        if background_method == BackgroundCorrection.EXP:
            self.exponential_correction(background1, background2, "ThO246 exp corrected", "counts normalised to time")
            self.exponential_correction(background1, background2, "ThO246 exp corrected sbm normalised" ,"peak cps normalised by sbm")
        elif background_method == BackgroundCorrection.LIN:
            self.linear_correction(background1, background2)
        elif background_method == BackgroundCorrection.CONST:
            self.constant_correction(background2)
        else:
            raise Exception("No background correction selected")

    def background_correction_all_peaks(self, background2):
        # if self.mpName not in mpNamesNonBackground:
        # raise Exception("Calling background subtraction on a background peak")
        self.data["sbm normalised background corrected all peaks"] = []
        self.data["background corrected all peaks"] = []
        cps = self.data["counts normalised to time"]
        cps_sbm = self.data["peak cps normalised by sbm"]

        bckgrd_cps = background2.data["counts normalised to time"]
        bckgrd_cps_sbm = background2.data["peak cps normalised by sbm"]

        for i, j in zip(cps, bckgrd_cps):
            i2 = i - j
            self.data["background corrected all peaks"].append(i2)

        for i, j in zip(cps_sbm, bckgrd_cps_sbm):
            i2 = i - j
            self.data["sbm normalised background corrected all peaks"].append(i2)

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

        for i, j, k in zip(cps, bckgrd1_cps, bckgrd2_cps):
            y1 = j
            y2 = k
            yThO246 = i

            isConstant = y2 >= y1
            if isConstant:
                yEstimatedBackground = y2

            else:
                # NOTE we shift the exponential curve to x1=0 to avoid "a" becoming too large
                xThO246 = xThO246 - x1
                a, b, yEstimatedBackground, yEstimatedBackgroundError = estimateExponential((0, y1), (x2 - x1, y2),
																							xThO246)
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
                self.data["expCorrectionFunction"] = lambda x: y2
            else:
                self.data["expCorrectionFunction"] = lambda x: gradient * x + c

    def constant_correction(self, background2):
        if self.mpName != "ThO246":
            raise Exception("Calling constant background subtraction on a non-ThO246 mass peak")
        pass

    # TODO

    ###################
    ### Not used yet###
    ###################

    def calculateMeanAndStDev(self, inputKey, outputKey):
        self.data[outputKey] = calculateOutlierResistantMeanAndStDev(self.rawRows[inputKey], NUMBER_OF_OUTLIERS_ALLOWED)

    def calculate_cps_mean_and_st_dev(self, countTime, inputKey, outputKey):
        mean, stDev = self.data[inputKey]
        cpsMean = mean * MEASUREMENTS_PER_SCAN_PER_MASS_PEAK / countTime
        cpsStDev = stDev * MEASUREMENTS_PER_SCAN_PER_MASS_PEAK / countTime
        self.data[outputKey] = cpsMean, cpsStDev

    def calculateBackgroundSubtractionSBM(self, sbmBackground):
        sbmMean, sbmStDev = self.data["sbm_cps"]
        self.data["sbmBackgroundCorrected"] = (sbmMean - sbmBackground, sbmStDev)

    def normalise_to_sbm(self):
        countsMean, countsStDev = self.data["cps"]
        sbmMean, sbmStDev = self.data["sbmBackgroundCorrected"]
        mean = countsMean / sbmMean
        stDev = mean * math.sqrt(
            (calculateRelativeErrors(sbmMean, sbmStDev) ** 2) + (calculateRelativeErrors(countsMean, countsStDev) ** 2))
        self.data["cps"] = mean, stDev

    def subtract_background2(self, background, mpNamesNonBackground):
        if self.mpName not in mpNamesNonBackground:
            raise Exception("Calling background subtraction on a background peak")

        backgroundMean, backgroundStDev = background.data["cps"]
        mean, stDev = self.data["cps"]
        correctedMean = mean - backgroundMean
        correctedStDev = math.sqrt((stDev ** 2) + (backgroundStDev ** 2))
        self.data["cpsBackgroundCorrected"] = correctedMean, correctedStDev
