from models.mathbot import *
from models.settings import *
import math

# contains the data for a single scan within a single mass peak within a spot
class Row:
	def __init__(self,spotName,mpName,scanNumber,massPeakValue,countData,sbmData):
		self.name = spotName + " " + mpName + " " + str(scanNumber)
		self.mpName = mpName
		self.scan_number = str(scanNumber)
		#self.time = timeOfScan
		self.massPeakValue = massPeakValue

		self.rawRows = {}
		self.rawRows["counts"] = countData
		self.rawRows["sbm"] = sbmData

		self.data = {}

	def __repr__(self):
		return self.name


	def calculateMeanAndStDev(self,inputKey,outputKey):
		self.data[outputKey]= calculateOutlierResistantMeanAndStDev(self.rawRows[inputKey], NUMBER_OF_OUTLIERS_ALLOWED)

	def calculate_cps_mean_and_st_dev(self, countTime, inputKey, outputKey):
		mean, stDev = self.data[inputKey]
		cpsMean = mean*MEASUREMENTS_PER_SCAN_PER_MASS_PEAK/countTime
		cpsStDev = stDev*MEASUREMENTS_PER_SCAN_PER_MASS_PEAK/countTime
		self.data[outputKey] = cpsMean, cpsStDev

	def calculateBackgroundSubtractionSBM(self,sbmBackground):
		sbmMean,sbmStDev = self.data["sbm_cps"]
		self.data["sbmBackgroundCorrected"] = (sbmMean - sbmBackground, sbmStDev)

	def normalise_to_sbm(self):
		countsMean, countsStDev = self.data["cps"]
		sbmMean, sbmStDev = self.data["sbmBackgroundCorrected"]
		mean = countsMean/sbmMean
		stDev = mean*math.sqrt((calculateRelativeErrors(sbmMean,sbmStDev)**2)+(calculateRelativeErrors(countsMean,countsStDev)**2))
		self.data["cps"] = mean,stDev

	def subtract_background2(self, background, mpNamesNonBackground):
		if self.mpName not in mpNamesNonBackground:
			raise Exception("Calling background subtraction on a background peak")

		backgroundMean,backgroundStDev = background.data["cps"]
		mean,stDev = self.data["cps"]
		correctedMean  = mean - backgroundMean
		correctedStDev = math.sqrt((stDev**2) + (backgroundStDev**2))
		self.data["cpsBackgroundCorrected"] = correctedMean,correctedStDev

	def subtract_linear_background(self, background1, background2):
		if self.mpName != "ThO246":
			raise Exception("Calling linear background subtraction on a non-ThO246 mass peak")
		x1 = background1.massPeakValue
		y1,y1Error = background1.data["cps"]
		x2 = background2.massPeakValue
		y2,y2Error = background2.data["cps"]
		xThO246 = self.massPeakValue
		yThO246, yThO246Error = self.data["cps"]

		isConstant = y2 >= y1
		if isConstant:
			yEstimatedBackground = y2
			yEstimatedBackgroundError = y2Error
		else:
			gradient = (y2-y1)/(x2-x1)
			c = y1 - gradient*x1
			yEstimatedBackground = gradient*xThO246 + c
			yEstimatedBackgroundError = math.sqrt((((x2-xThO246)/(x2-x1))*y1Error)**2 + (((xThO246 - x1)/(x2-x1))*y2Error)**2)
			#print(y1, " ", y2, " ", yEstimatedBackground)
			#print(y1Error," ", y2Error, " ", yEstimatedBackgroundError)

		correctedBackgroundExponentialThO246 = yThO246 - yEstimatedBackground
		correctedBackgroundExponentialThO246Error = errors_in_quadrature([yEstimatedBackgroundError, yThO246Error])
		#print(correctedBackgroundExponentialThO246," ", correctedBackgroundExponentialThO246Error)

		self.data["cpsBackgroundCorrected"] = correctedBackgroundExponentialThO246, correctedBackgroundExponentialThO246Error

	def subtractExponentialBackground(self,background1,background2):
		if self.mpName != "ThO246":
			raise Exception("Calling exponential background subtraction on a non-ThO246 mass peak")

		x1 = background1.massPeakValue
		y1,y1Error = background1.data["cps"]
		x2 = background2.massPeakValue
		y2,y2Error = background2.data["cps"]
		xThO246 = self.massPeakValue
		yThO246, yThO246Error = self.data["cps"]		

		isConstant = y2 >= y1
		if isConstant:
			yEstimatedBackground = y2
			yEstimatedBackgroundError = y2Error
		else:
			#NOTE we shift the exponential curve to x1=0 to avoid "a" becoming too large
			xThO246 = xThO246 - x1
			a, b, yEstimatedBackground, yEstimatedBackgroundError = estimateExponential((0,y1),y1Error,(x2-x1,y2),y2Error,xThO246)
		correctedBackgroundExponentialThO246 = yThO246 - yEstimatedBackground
		correctedBackgroundExponentialThO246Error = math.sqrt((yEstimatedBackgroundError**2)+(yThO246Error**2))



		self.data["cpsBackgroundCorrected"] = correctedBackgroundExponentialThO246,correctedBackgroundExponentialThO246Error
		if isConstant:
			self.data["expCorrectionFunction"] = lambda x: y2
		else:
			self.data["expCorrectionFunction"] = lambda x: a*math.exp(b*(x-x1))
