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

	def normalise_all_counts_to_cps(self):
		for row in self.rows:
			row.normalise_all_counts_to_cps(self.count_time)

	def normalise_peak_cps_by_sbm(self):
		for row in self.rows:
			row.normalise_peak_cps_by_sbm()

	def calculate_outlier_resistant_mean_st_dev_for_rows(self, input_key, output_key):
		for row in self.rows:
			row.calculate_mean_and_st_dev_blocks(input_key, output_key)

	def background_correction_230Th(self, background_method, background1, background2):
		for row, row_b1, row_b2 in zip(self.rows, background1.rows, background2.rows):
			row.background_correction_230Th(background_method, row_b1, row_b2)

	def background_correction_all_peaks(self, background2):
		for row, row_b2 in zip(self.rows, background2.rows):
			row.background_correction_all_peaks(row_b2)

	###################
	### Not used yet###
	###################



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
		