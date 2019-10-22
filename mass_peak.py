from mathbot import *
from row import Row
import math



# contains the data for a single mass peak within a spot
class MassPeak:
	def __init__(self,spotName,mpName,massPeakValues,countRowData,sbmRowData, countTime, numberOfScans):
		self.name = spotName + " " + mpName
		self.mpName = mpName
		self.rows = []
		self.countTime = countTime
		for i in range(numberOfScans):
			row = Row(spotName,mpName,i,massPeakValues[i],countRowData[i],sbmRowData[i])
			self.rows.append(row)
		self.data = {}

	def __repr__(self):
		return self.name


	def calculateMeanAndStDevForRows(self,inputKey,outputKey):
		for row in self.rows:
			row.calculateMeanAndStDev(inputKey,outputKey)

	def calculateCpsMeanAndStDevForRows(self, inputKey, outputKey):
		for row in self.rows:
			row.calculate_cps_mean_and_st_dev(self.countTime, inputKey, outputKey)

	def calculateBackgroundSubtractionSBMForRows(self, sbmBackground):
		for row in self.rows:
			row.calculateBackgroundSubtractionSBM(sbmBackground)

	def normaliseToSBMForRows(self):
		for row in self.rows:
			row.normalise_to_sbm()

	def subtractBackground2ForRows(self,backgroundMassPeak):
		for row, backgroundRow in zip(self.rows, backgroundMassPeak.rows):
			row.subtract_background2(backgroundRow)

	def subtract_linear_background_for_rows(self,background1MassPeak,background2MassPeak):
		for row, background1Row, background2Row in zip(self.rows, background1MassPeak.rows, background2MassPeak.rows):
			row.subtract_linear_background(background1Row,background2Row)

	def subtractExponentialBackgroundForRows(self,background1MassPeak,background2MassPeak):
		for row, background1Row, background2Row in zip(self.rows, background1MassPeak.rows, background2MassPeak.rows):
			row.subtractExponentialBackground(background1Row,background2Row)

	def calculateErrorWeightedMeanAndStDevForScans(self):
		rowData = [row.data["cpsBackgroundCorrected"] for row in self.rows]
		means = [mean for mean,stDev in rowData]
		stDevs = [stDev for mean,stDev in rowData]
		self.data["cpsErrorWeighted"] = calculateErrorWeightedMeanAndStDev(means,stDevs)
		