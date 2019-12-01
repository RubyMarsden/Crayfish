import csv

from configuration import *
from shrimp_spot import *
from spot_plot import *
from mathbot import weightedRegression

#mp stands for massPeak

DECIMAL_PLACES = 3
STANDARD_PREFIX = "R33"
SAMPLE_PREFIX1 = "545"
SAMPLE_PREFIX2 = "428"
SAMPLE_PREFIX3 = "812"
SAMPLE_PREFIX4 = "366"
SAMPLE_PREFIX5 = "566"
FILE_NAME = 'data/rm_k6_19080820_b.csv'

# loads in the CSV data and creates a list of spots out of them
def loadSpots():
	#import csv of pd data
	with open(FILE_NAME, newline='') as csvfile:
	    csvStringData = list(csv.reader(csvfile))

	#making a list of spots (it's empty now)
	spots = []
	currentLineNumber = 2;
	spotData = []
	while currentLineNumber < len(csvStringData):
		while currentLineNumber < len(csvStringData) and csvStringData [currentLineNumber][0] != "***" :
			spotData.append(csvStringData[currentLineNumber])
			currentLineNumber = currentLineNumber + 1

		spots.append(Spot(spotData))
		spotData = []
		currentLineNumber += 1
	return spots

#not perfect - could cause problems because in does not test if only at beginning.
def findSpotsByPrefix(spots,prefix):
	groupSpots = []
	for spot in spots:
		if spot.name.startswith(prefix):
			groupSpots.append(spot)
	return groupSpots


#Activity ratio returns a pair with (x,xerror) sorry!
def spotLinearRegression(spots,fitIntercept):
	xs = [spot.data["UThActivityRatio"][0] for spot in spots]
	ys = [spot.data["ThThActivityRatio"][0] for spot in spots]
	xEs = [spot.data["UThActivityRatio"][1] for spot in spots]
	yEs = [spot.data["ThThActivityRatio"][1] for spot in spots]
	c, m = weightedRegression(xs,ys,xEs,yEs,fitIntercept)
	return xs,ys,xEs,yEs,float(c),float(m[0])

def calculateSpotAge(spot,WR):
	x1 = spot.data["UThActivityRatio"][0]
	x1_error = spot.data["UThActivityRatio"][1]
	y1 = spot.data["ThThActivityRatio"][0]
	y1_error = spot.data["ThThActivityRatio"][1]
	x2 = WR
	y2 = WR
	m = (y1-y2)/(x1-x2)
	error_m = math.sqrt((x1_error/x1)**2 + (y1_error/y1)**2)
	age = ageFromGradient(m,TH230_DECAY_CONSTANT)
	age_error = error_m * age
	print(x1_error," ", y1_error," ", error_m)
	return age, age_error

def format(v):
	return round(v, DECIMAL_PLACES)

configurations = []
configurations.append(Configuration(True, True))
configurations.append(Configuration(True, False))
configurations.append(Configuration(False, True))
configurations.append(Configuration(False, False))



def processData(config):
	spots = loadSpots()
	for spot in spots:
		spot.calculateMeanAndStDevForRows("counts", "counts")
		spot.calculateCpsMeanAndStDevForRows("counts", "cps")

		if config.normaliseBySBM:
			spot.calculateMeanAndStDevForRows("sbm", "sbm")
			spot.calculateCpsMeanAndStDevForRows("sbm", "sbm_cps")
			spot.calculateBackgroundSubtractionSBMForRows()
			spot.normaliseToSBMForRows()

		if config.linear_background_correction:
			spot.subtract_linear_background_for_rows()
			#spot.subtractExponentialBackgroundForRows()
		else:
			spot.subtractBackground2ForRows()			

		spot.calculateErrorWeightedMeanAndStDevForScans()
		spot.calculateActivityRatio()
	return spots

print("Starting crayfish")
print("Loading data from " + FILE_NAME)

normaliseBySBM = input("Do you want to normalise by the SBM as a proxy for primary beam strength? Y/N (type and then enter).")
backgroundCorrectionType = input("Which background correction is required for the 230 Th peak? 0 for no extra correction, 1 for linear correction and 2 for both corrections to compare.")

config = Configuration(normaliseBySBM is "Y", backgroundCorrectionType is "1")
spots = processData(config)

# 	plotExponentialBackground(spot, onSameGraph=True)
standardSpots = findSpotsByPrefix(spots,STANDARD_PREFIX)
#standardLinearRegression = spotLinearRegression(standardSpots,False)
sampleSpots = findSpotsByPrefix(spots,SAMPLE_PREFIX1) + findSpotsByPrefix(spots,SAMPLE_PREFIX2) + findSpotsByPrefix(spots,SAMPLE_PREFIX3) + findSpotsByPrefix(spots,SAMPLE_PREFIX4) + findSpotsByPrefix(spots,SAMPLE_PREFIX5)
#sampleLinearRegression = spotLinearRegression(sampleSpots,True)


#plotLinearRegressionWithData(STANDARD_PREFIX,*standardLinearRegression)
#showPlot()

#plotLinearRegressionWithData(SAMPLE_PREFIX1+" "+SAMPLE_PREFIX2,*sampleLinearRegression)
#plotLine(*standardLinearRegression[4:6],0,max(sampleLinearRegression[0]))
#showPlot()

#write data to csv file
with open('crayfish_output.csv','w', newline='') as csvfile:
	wr = csv.writer(csvfile, delimiter=',')
	wr.writerow(["Spot name", "Age", "Error", "Age SBM", "Error"])
	for spot in sampleSpots:
		wr.writerow([spot.name, calculateSpotAge(spot, WR_SS14_28)[0],calculateSpotAge(spot, WR_SS14_28)[1], spot.data["UThActivityRatio"], spot.data["ThThActivityRatio"]])
	csvfile.close()

with open('crayfish_rows.csv', 'w', newline='') as csvfile:
	wr = csv.writer(csvfile, delimiter=",")
	wr.writerow(["Spot name", "Mass peak name", "Scan number", "cps", "cps error", "Mass peak value"])
	for spot in spots:
		for mpName in spot.massPeaks:
			for row in spot.massPeaks[mpName].rows:
				wr.writerow([spot.name,mpName,row.scan_number, row.data["cps"][0], row.data["cps"][1], row.massPeakValue])
	csvfile.close()