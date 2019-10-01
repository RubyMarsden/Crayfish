from mathbot import *
from settings import *
import math

# contains the data for a single scan within a single mass peak within a spot
class Row:
	def __init__(self,spotName,mpName,scanNumber,massPeakValue,countData,sbmData):
		self.name = spotName + " " + mpName + " " + str(scanNumber)
		self.mpName = mpName
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
		
	def calculateBackgroundSubtractionSBM(self,sbmBackground):
		sbmMean,sbmStDev = self.data["sbm"]
		self.data["sbmBackgroundCorrected"] = (sbmMean - sbmBackground, sbmStDev)

	def calculateCpsMeanAndStDev(self,countTime):
		mean,stDev = self.data["counts"]
		cpsMean = mean*MEASUREMENTS_PER_SCAN_PER_MASS_PEAK/countTime
		cpsStDev = stDev*MEASUREMENTS_PER_SCAN_PER_MASS_PEAK/countTime
		self.data["cps"] = cpsMean,cpsStDev

	def normaliseToSBM(self):
		countsMean, countsStDev = self.data["counts"]
		sbmMean, sbmStDev = self.data["sbmBackgroundCorrected"]
		mean = countsMean/sbmMean
		stDev = mean*math.sqrt((calculateRelativeErrors(sbmMean,sbmStDev)**2)+(calculateRelativeErrors(countsMean,countsStDev)**2))
		self.data["cps"] = mean,stDev


	def subtractBackground2(self,background):
		if self.mpName not in NONBACKGROUND:
			raise Exception("Calling background subtraction on a background peak")

		backgroundMean,backgroundStDev = background.data["cps"]
		mean,stDev = self.data["cps"]
		correctedMean  = mean - backgroundMean
		correctedStDev = math.sqrt((stDev**2) + (backgroundStDev**2))
		self.data["cpsBackgroundCorrected"] = correctedMean,correctedStDev

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
