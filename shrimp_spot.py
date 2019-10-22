from mathbot import *
from mass_peak import MassPeak
from settings import *
import math


#making a class called spot
class Spot:
	def __init__(self, spotData):
		self.name = spotData [0][0]
		self.numberOfScans = int(spotData[1][4])
		self.numberOfPeaks = int(spotData[1][6])
		self.sbmBackground = int(spotData[1][15])
		self.mpNames = [row[0] for row in spotData [4:4+self.numberOfPeaks]]
		self.mpCountTimes = {self.mpNames[i] : int(spotData[i+4][3]) for i in range(0,self.numberOfPeaks)}
		
		self.massPeaks = {}
		self.data = {}
		
		for i in range(0, self.numberOfPeaks):
			ithMpRows = []
			ithMpXValues = []
			ithSbmRows = []
			lineNumber = self.numberOfPeaks+5 + i*2
			mpName = self.mpNames[i]
			while lineNumber < len(spotData) - 1:
				row = [float(value) for value in spotData[lineNumber][4:4+self.numberOfScans]]
				row2 = [int(value) for value in spotData[lineNumber+1][1:1+self.numberOfScans]]
				ithMpRows.append(row)
				ithMpXValues.append(float(spotData[lineNumber][1]))
				ithSbmRows.append(row2)
				lineNumber += self.numberOfPeaks*2

			massPeak = MassPeak(self.name,mpName,ithMpXValues,ithMpRows,ithSbmRows, self.mpCountTimes[mpName],self.numberOfScans)
			self.massPeaks[mpName] = massPeak

	def __repr__(self):
		return self.name

	def calculateMeanAndStDevForRows(self,inputKey,outputKey):
		for mp in self.massPeaks.values():
			mp.calculateMeanAndStDevForRows(inputKey,outputKey)

	def calculateCpsMeanAndStDevForRows(self, inputKey, outputKey):
		for mp in self.massPeaks.values():
			mp.calculateCpsMeanAndStDevForRows(inputKey, outputKey)

	def calculateBackgroundSubtractionSBMForRows(self):
		for mp in self.massPeaks.values():
			mp.calculateBackgroundSubtractionSBMForRows(self.sbmBackground)

	def normaliseToSBMForRows(self):
		for mp in self.massPeaks.values():
			mp.normaliseToSBMForRows()

	def subtractBackground2ForRows(self):
		for mp in self.massPeaks.values():
			if mp.mpName in NONBACKGROUND:
				mp.subtractBackground2ForRows(self.massPeaks[BACKGROUND2])

	def subtract_linear_background_for_rows(self):
		for mp in self.massPeaks.values():
			if mp.mpName == "ThO246":
				mp.subtract_linear_background_for_rows(self.massPeaks[BACKGROUND1],self.massPeaks[BACKGROUND2])
			elif mp.mpName in NONBACKGROUND:
				mp.subtractBackground2ForRows(self.massPeaks[BACKGROUND2])

	def subtractExponentialBackgroundForRows(self):
		for mp in self.massPeaks.values():
			if mp.mpName == "ThO246":
				mp.subtractExponentialBackgroundForRows(self.massPeaks[BACKGROUND1],self.massPeaks[BACKGROUND2])
			elif mp.mpName in NONBACKGROUND:
				mp.subtractBackground2ForRows(self.massPeaks[BACKGROUND2])

	def calculateErrorWeightedMeanAndStDevForScans(self):
		for mpName in NONBACKGROUND:
			self.massPeaks[mpName].calculateErrorWeightedMeanAndStDevForScans()
		
	def calculateActivityRatio(self):
		ThO246 = self.massPeaks["ThO246"]
		ThO248 = self.massPeaks["ThO248"]
		UO254 = self.massPeaks["UO254"]
		key = "cpsErrorWeighted"
		self.data["ThThActivityRatio"]= activityRatio(*ThO246.data[key],TH230_DECAY_CONSTANT,TH230_DECAY_CONSTANT_ERROR, *ThO248.data[key],TH232_DECAY_CONSTANT, TH232_DECAY_CONSTANT_ERROR)
		self.data["UThActivityRatio"] = activityRatio(*UO254.data[key],U238_DECAY_CONSTANT,U238_DECAY_CONSTANT_ERROR, *ThO248.data[key],TH232_DECAY_CONSTANT, TH232_DECAY_CONSTANT_ERROR)
		