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
SAMPLE_PREFIX5 = "test"
FILE_NAME = 'data/test.csv'

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
	y1 = spot.data["ThThActivityRatio"][0]
	x2 = WR
	y2 = WR
	m = (y1-y2)/(x1-x2)
	print(x1, x2, y1,y2,m)
	age = ageFromGradient(m,TH230_DECAY_CONSTANT)
	return age

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
	
		if config.normaliseBySBM:
			spot.calculateMeanAndStDevForRows("sbm", "sbm")	
			spot.calculateBackgroundSubtractionSBMForRows()
			spot.normaliseToSBMForRows()
		else:
			spot.calculateCpsMeanAndStDevForRows()

		if config.expBackgroundCorrection:
			spot.subtractExponentialBackgroundForRows()
		else:
			spot.subtractBackground2ForRows()			

		spot.calculateErrorWeightedMeanAndStDevForScans()
		spot.calculateActivityRatio()
	return spots

print("Starting crayfish")
print("Loading data from " + FILE_NAME)

normaliseBySBM = input("Do you want to normalise by the SBM as a proxy for primary beam strength? Y/N (type and then enter).")
backgroundCorrectionType = input("Which background correction is required for the 230 Th peak? 0 for no extra correction, 1 for exponential correction and 2 for linear correction and 3 for all corrections to compare.")

config = Configuration(normaliseBySBM is "Y", backgroundCorrectionType is 1)
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
with open('crayfish_output.csv','w') as csvfile:
	wr = csv.writer(csvfile, delimiter=' ')#, quotechar='|', quoting=csv.QUOTE_MINIMAL)
	for spot in sampleSpots:
		wr.writerow([spot.name," ", calculateSpotAge(spot,WR_SS15_45), spot.data["UThActivityRatio"], spot.data["ThThActivityRatio"]])
	#wr.writerow(["hello"])
	csvfile.close()