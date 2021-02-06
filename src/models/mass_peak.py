from models.mathbot import *
from models.row import Row
import math


# contains the data for a single mass peak within a spot
class MassPeak:
    def __init__(self, spotName, mpName, massPeakValues, countRowData, sbmRowData, countTime, numberOfScans):
        self.name = spotName + " " + mpName
        self.mpName = mpName
        self.rows = []
        self.count_time = countTime
        for i in range(numberOfScans):
            row = Row(spotName, mpName, i, massPeakValues[i], countRowData[i], sbmRowData[i])
            self.rows.append(row)

    def __repr__(self):
        return self.name

    def standardise_sbm_and_subtract_sbm_background(self, sbm_background):
        for row in self.rows:
            row.standardise_sbm_and_subtract_sbm_background(sbm_background, self.count_time)

    def get_sbm_time_series(self, row_number, start_time):
        row = self.rows[row_number]
        return row.get_local_sbm_time_series(self.count_time, start_time)

    def normalise_all_counts_to_cps(self, config):
        for row in self.rows:
            row.normalise_all_counts_to_cps(config, self.count_time)

    def calculate_outlier_resistant_mean_st_dev_for_rows(self, config):
        for row in self.rows:
            row.calculate_mean_and_st_dev_blocks(config)

    def background_correction_230Th(self, config, background_method, background1, background2):
        for row, row_b1, row_b2 in zip(self.rows, background1.rows, background2.rows):
            row.background_correction_230Th(config, background_method, row_b1, row_b2)

    def background_correction_all_peaks(self, config, background2):
        for row, row_b2 in zip(self.rows, background2.rows):
            row.constant_background_correction(config, row_b2)
