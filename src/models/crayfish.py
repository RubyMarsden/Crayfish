import csv

from configuration import *
from shrimp_spot import *
from spot_plot import *
from mathbot import weightedRegression

# mp stands for massPeak

DECIMAL_PLACES = 3
STANDARD_PREFIXES = ["R33"]
SAMPLE_PREFIXES = ["R33", "428", "PL", "G4", "545", "566", "366", "812", "GJ", "P1"]
FILE_NAME = 'data/test.csv'


# loads in the CSV data and creates a list of spots out of them
def loadSpots(config):
    print("Loading data from " + config.input_file)
    # import csv of pd data
    with open(config.input_file, newline='') as csvfile:
        csvStringData = list(csv.reader(csvfile))

    #finding the first spot
    currentLineNumber = 0;
    while csvStringData[currentLineNumber][0] != "***":
        currentLineNumber += 1
    currentLineNumber += 1

    # making a list of spots (it's empty now)
    spots = []
    spotData = []
    while currentLineNumber < len(csvStringData):
        while currentLineNumber < len(csvStringData) and csvStringData[currentLineNumber][0] != "***":
            spotData.append(csvStringData[currentLineNumber])
            currentLineNumber = currentLineNumber + 1
        spot = Spot(spotData, config)
        spots.append(spot)
        spotData = []
        currentLineNumber += 1
    return spots


def write_csv_rows(spots, output_file):
    with open(output_file, 'w', newline='') as csvfile:
        wr = csv.writer(csvfile, delimiter=",")
        wr.writerow(["Spot name", "Mass peak name", "Scan number", "cps", "cps error", "Mass peak value"])
        for spot in spots:
            for mpName in spot.massPeaks:
                for row in spot.massPeaks[mpName].rows:
                    wr.writerow(
                        [spot.name, mpName, row.scan_number, row.data["cps"][0], row.data["cps"][1], row.massPeakValue])
        csvfile.close()


def write_csv_ages(spots, output_file):
    # write data to csv file
    with open(output_file, 'w', newline='') as csvfile:
        wr = csv.writer(csvfile, delimiter=',')
        wr.writerow(["Spot name", "Age", "Error", "UTh Activity", "ThTh Activity"])
        for spot in spots:
            if spot.is_sample:
                wr.writerow([spot.name, calculateSpotAge(spot, WR_SS14_28)[0], calculateSpotAge(spot, WR_SS14_28)[1],
                             spot.data["UThActivityRatio"], spot.data["ThThActivityRatio"]])
        csvfile.close()


# Activity ratio returns a pair with (x,xerror) sorry!
def spotLinearRegression(spots, fitIntercept):
    xs = [spot.data["UThActivityRatio"][0] for spot in spots]
    ys = [spot.data["ThThActivityRatio"][0] for spot in spots]
    xEs = [spot.data["UThActivityRatio"][1] for spot in spots]
    yEs = [spot.data["ThThActivityRatio"][1] for spot in spots]
    c, m = weightedRegression(xs, ys, xEs, yEs, fitIntercept)
    return xs, ys, xEs, yEs, float(c), float(m[0])


def calculateSpotAge(spot, WR):
    x1 = spot.data["UThActivityRatio"][0]
    x1_error = spot.data["UThActivityRatio"][1]
    if spot.uranium_peak_name == "UO251":
        x1 *= U235_U238_RATIO
        x1_error *= U235_U238_RATIO
    y1 = spot.data["ThThActivityRatio"][0]
    y1_error = spot.data["ThThActivityRatio"][1]
    x2 = WR
    y2 = WR
    m = (y1 - y2) / (x1 - x2)
    error_m = math.sqrt((x1_error / x1) ** 2 + (y1_error / y1) ** 2)
    age = ageFromGradient(m, TH230_DECAY_CONSTANT)
    age_error = error_m * age
    return age, age_error


def format(v):
    return round(v, DECIMAL_PLACES)


def processData(config, spots):
    for spot in spots:
        spot.calculate_outlier_resistant_mean_st_dev_for_rows("counts", "counts")
        spot.calculate_outlier_resistant_mean_st_dev_for_rows("counts", "cps")

        if config.normaliseBySBM:
            spot.calculate_outlier_resistant_mean_st_dev_for_rows("sbm", "sbm")
            spot.calculate_outlier_resistant_mean_st_dev_for_rows("sbm", "sbm_cps")
            spot.calculateBackgroundSubtractionSBMForRows()
            spot.normaliseToSBMForRows()

        if config.exponential_background_correction:
            spot.subtractExponentialBackgroundForRows()
        else:
            spot.subtractBackground2ForRows()

        spot.calculate_error_weighted_mean_and_st_dev_for_ages()
        spot.calculateActivityRatio()
    return spots


def run(config):
    spots = loadSpots(config)
    processData(config, spots)
    write_csv_rows(spots, config.row_output_file)
    write_csv_ages(spots, config.age_output_file)


if __name__ == "__main__":
    print("Starting crayfish")

    normaliseBySBM = input(
        "Do you want to normalise by the SBM as a proxy for primary beam strength? Y/N (type and then enter).")
    backgroundCorrectionType = input(
        "Which background correction is required for the 230 Th peak? 0 for no extra correction, 1 for linear correction and 2 for both corrections to compare.")
    input_file = "data/rm_k6.csv"
    row_output_file = "row_output.csv"
    age_output_file = "age_output.csv"
    config = Configuration(
        normaliseBySBM is "Y",
        backgroundCorrectionType is "1",
        SAMPLE_PREFIXES,
        STANDARD_PREFIXES,
        input_file,
        row_output_file,
        age_output_file
    )
    run(config)

    # plotExponentialBackground(spot, onSameGraph=True)
    # standardLinearRegression = spotLinearRegression(standardSpots,False)
    # sampleLinearRegression = spotLinearRegression(sampleSpots,True)

    # plotLinearRegressionWithData(STANDARD_PREFIX,*standardLinearRegression)
    # showPlot()

    # plotLinearRegressionWithData(SAMPLE_PREFIX1+" "+SAMPLE_PREFIX2,*sampleLinearRegression)
    # plotLine(*standardLinearRegression[4:6],0,max(sampleLinearRegression[0]))
    # showPlot()

