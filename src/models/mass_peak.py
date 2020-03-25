from models.mathbot import *
from models.row import Row
import math



# contains the data for a single mass peak within a spot
class MassPeak:
	def __init__(self,spotName,mpName,massPeakValues,countRowData,sbmRowData, countTime, numberOfScans):
		self.name = spotName + " " + mpName
		self.mpName = mpName
		self.rows = []
		self.count_time = countTime
		for i in range(numberOfScans):
			row = Row(spotName,mpName,i,massPeakValues[i],countRowData[i],sbmRowData[i])
			self.rows.append(row)
		self.data = {}

	def __repr__(self):
		return self.name

	def normalise_sbm_and_subtract_sbm_background(self, sbm_background):
		for row in self.rows:
			row.normalise_sbm_and_subtract_sbm_background(sbm_background, self.count_time)

	def get_sbm_time_series(self, row_number, start_time):
		row = self.rows[row_number]
		return row.get_local_sbm_time_series(self.count_time, start_time)

	###################
	### Not used yet###
	###################

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

	def subtractBackground2ForRows(self,backgroundMassPeak, mpNamesNonBackground):
		for row, backgroundRow in zip(self.rows, backgroundMassPeak.rows):
			row.subtract_background2(backgroundRow, mpNamesNonBackground)

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
		