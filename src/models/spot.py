from datetime import datetime

from models.mathbot import *
from models.mass_peak import MassPeak
from models.row import DataKey
from models.settings import *

class Spot:

	def __init__(self, spot_data):

		self.name = spot_data[0][0]
		parts = self.name.split("-",1)
		if len(parts) != 2:
			raise Exception("None standard spot name in file '" + self.name + "'. Spot names must be of the form (SAMPLE)-(ID)")
		self.sample_name, self.id = parts

		self.date_and_time = self._parse_datetime(spot_data[0][1], spot_data[0][2])

		self.numberOfScans = int(spot_data[1][4])
		self.numberOfPeaks = int(spot_data[1][6])
		self.sbmBackground = int(spot_data[1][15])
		self.mpNames = [row[0] for row in spot_data [4:4 + self.numberOfPeaks]]
		self.mpNamesBackground = [BACKGROUND1, BACKGROUND2]
		self.mpNamesNonBackground = [name for name in self.mpNames if name not in self.mpNamesBackground]
		self.uranium_peak_name = self.find_uranium_peak_name()
		self.mpCountTimes = {self.mpNames[i] : int(spot_data[i + 4][3]) for i in range(0, self.numberOfPeaks)}

		self.massPeaks = {}
		self.data = {}
		spot_number_of_rows = 5 + self.numberOfPeaks + self.numberOfScans * 2 * self.numberOfPeaks
		for i in range(0, self.numberOfPeaks):
			ithMpRows = []
			ithMpXValues = []
			ithSbmRows = []
			lineNumber = self.numberOfPeaks+5 + i*2
			mpName = self.mpNames[i]
			while lineNumber < spot_number_of_rows - 1:
				mass_peak_row = [float(value) for value in spot_data[lineNumber][4:14]]
				sbm_row = [int(value) for value in spot_data[lineNumber + 1][1:11]]
				ithMpRows.append(mass_peak_row)
				ithMpXValues.append(float(spot_data[lineNumber][1]))
				ithSbmRows.append(sbm_row)
				lineNumber += self.numberOfPeaks*2

			massPeak = MassPeak(self.name,mpName,ithMpXValues,ithMpRows,ithSbmRows, self.mpCountTimes[mpName],self.numberOfScans)
			self.massPeaks[mpName] = massPeak

		self.count_time_duration = sum([massPeak.count_time for massPeak in self.massPeaks.values()])*self.numberOfScans

		self.errors_by_scan = {}

		self.sbm_time_series = None

		self.is_flagged = False

	def _parse_datetime(self, date_str, time_str):
		day, month, year = [int(i) for i in date_str.split("/")]
		split_time = [int(i) for i in time_str.split(":")]
		if len(split_time) == 2:
			hour, minute = split_time
			second = 0
		else:
			hour, minute, second = split_time

		return datetime(year, month, day, hour, minute, second)

	def __repr__(self):
		return self.name

	def standardise_sbm_and_subtract_sbm_background(self):
		for massPeak in self.massPeaks.values():
			massPeak.standardise_sbm_and_subtract_sbm_background(self.sbmBackground)

	def calculate_sbm_time_series(self):
		self.sbm_time_series = []
		current_time = 0
		for i in range(self.numberOfScans):
			for massPeak in self.massPeaks.values():
				self.sbm_time_series.extend(massPeak.get_sbm_time_series(i, current_time))
				current_time += massPeak.count_time

	def normalise_all_counts_to_cps(self):
		for massPeak in self.massPeaks.values():
			massPeak.normalise_all_counts_to_cps()

	def normalise_peak_cps_by_sbm(self):
		for massPeak in self.massPeaks.values():
			massPeak.normalise_peak_cps_by_sbm()

	def calculate_outlier_resistant_mean_st_dev_for_rows(self):
		for mp in self.massPeaks.values():
			mp.calculate_outlier_resistant_mean_st_dev_for_rows()

	def background_correction(self, background_method, background1, background2):
		for massPeak in self.massPeaks.values():
			if massPeak.mpName == "ThO246":
				massPeak.background_correction_230Th(background_method, background1, background2)
			elif massPeak.mpName in self.mpNamesNonBackground:
				massPeak.background_correction_all_peaks(background2)

	def calculate_activity_ratios(self):
		# TODO sbm normalisation
		Th230_Th232_activity_ratios = []
		U238_Th232_activity_ratios = []

		U = self.massPeaks[self.uranium_peak_name]
		Th230 = self.massPeaks["ThO246"]
		Th232 = self.massPeaks["ThO248"]
		for i in range(self.numberOfScans):
			U_mean, U_stdev = U.rows[i].data[DataKey.BKGRD_CORRECTED]
			Th230_mean, Th230_stdev = Th230.rows[i].data[DataKey.BKGRD_CORRECTED]
			Th232_mean, Th232_stdev = Th232.rows[i].data[DataKey.BKGRD_CORRECTED]
			if U_mean <= 0 or U_stdev < 0 or Th230_mean <= 0 or Th230_stdev < 0 or Th232_mean <= 0 or Th232_stdev < 0:
				self.errors_by_scan[i] = "Error!"
				continue
			self.errors_by_scan[i] = "Data"
			Th230_Th232_activity, Th230_Th232_activity_uncertainty = activity_ratio(
				cps_mass_1=Th230_mean,
				cps_mass_1_uncertainty=Th230_stdev,
				decay_constant_1=TH230_DECAY_CONSTANT,
				decay_constant_1_uncertainty=TH230_DECAY_CONSTANT_ERROR,
				cps_mass_2=Th232_mean,
				cps_mass_2_uncertainty=Th232_stdev,
				decay_constant_2=TH232_DECAY_CONSTANT,
				decay_constant_2_uncertainty=TH232_DECAY_CONSTANT_ERROR
			)

			if self.uranium_peak_name == "UO254" or "U238":
				U238_mean = U_mean
				U238_stdev = U_stdev
			elif self.uranium_peak_name == "UO251" or "U235":
				U238_mean = U_mean * U235_U238_RATIO
				U238_stdev = U_stdev * U235_U238_RATIO
			else:
				raise Exception("Don't know what U isotope is used")

			U238_Th232_activity, U238_Th232_activity_uncertainty = activity_ratio(
				cps_mass_1=U238_mean,
				cps_mass_1_uncertainty=U238_stdev,
				decay_constant_1=U238_DECAY_CONSTANT,
				decay_constant_1_uncertainty=U238_DECAY_CONSTANT_ERROR,
				cps_mass_2=Th232_mean,
				cps_mass_2_uncertainty=Th232_stdev,
				decay_constant_2=TH232_DECAY_CONSTANT,
				decay_constant_2_uncertainty=TH232_DECAY_CONSTANT_ERROR
			)

			Th230_Th232_activity_ratios.append((Th230_Th232_activity, Th230_Th232_activity_uncertainty))
			U238_Th232_activity_ratios.append((U238_Th232_activity, U238_Th232_activity_uncertainty))

		self.data["(230Th_232Th)"] = Th230_Th232_activity_ratios
		self.data["(238U_232Th)"] = U238_Th232_activity_ratios

	def find_uranium_peak_name(self):
		for name in self.mpNamesNonBackground:
			if name.startswith("UO"):
				return name

		raise Exception("NO UO PEAK FOR SPOT " + self.name)

	def age_calculation(self, WR_value, WR_uncertainty, standard_line, standard_line_uncertainty):
		ages = []
		U238_Th232_activity_ratios = self.data["(238U_232Th)"]
		Th230_Th232_activity_ratios = self.data["(230Th_232Th)"]

		for (x, dx), (y, dy) in zip(U238_Th232_activity_ratios, Th230_Th232_activity_ratios):
			age, uncertainty = calculate_age_from_values(x, dx, y, dy, WR_value, WR_uncertainty, standard_line, standard_line_uncertainty)
			ages.append((age, uncertainty))

		self.data["ages"] = ages


	def calculate_error_weighted_mean_and_st_dev_for_ages(self):
		ages = []
		uncertainties = []
		for (i, j) in self.data["ages"]:
			if i is None or j is None:
				continue
			ages.append(i)
			uncertainties.append(j)

		age, uncertainty = calculate_error_weighted_mean_and_st_dev(ages, uncertainties)

		self.data["weighted age"] = (age, uncertainty)
		print(self.name, self.data["weighted age"])
