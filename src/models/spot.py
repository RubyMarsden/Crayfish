from datetime import datetime

from models.mathbot import *
from models.mass_peak import MassPeak
from models.data_key import DataKey
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

	def setup_new_calculation(self, configurations):
		self.data = {}
		for config in configurations:
			self.data[config] = {}
		for mp in self.massPeaks.values():
			for row in mp.rows:
				row.setup_new_calculation(configurations)

	def _parse_datetime(self, date_str, time_str):
		date = self._parse_date(date_str)

		split_time = [int(i) for i in time_str.split(":")]
		if len(split_time) == 2:
			hour, minute = split_time
			second = 0
		else:
			hour, minute, second = split_time

		return datetime(date.year, date.month, date.day, hour, minute, second)

	def _parse_date(self, date_str):
		for fmt in ('%Y-%m-%d,', '%d/%m/%Y'):
			try:
				return datetime.strptime(date_str, fmt)
			except ValueError:
				pass
		raise ValueError(f'no valid date format found for {date_str}')

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

	def normalise_all_counts_to_cps(self, config):
		for massPeak in self.massPeaks.values():
			massPeak.normalise_all_counts_to_cps(config)

	def calculate_outlier_resistant_mean_st_dev_for_rows(self, config):
		for mp in self.massPeaks.values():
			mp.calculate_outlier_resistant_mean_st_dev_for_rows(config)

	def background_correction(self, config, background1, background2):
		for massPeak in self.massPeaks.values():
			if massPeak.mpName == "ThO246":
				massPeak.background_correction_230Th(config, background1, background2)
			elif massPeak.mpName in self.mpNamesNonBackground:
				massPeak.background_correction_all_peaks(config, background2)

	def calculate_activity_ratios(self, config):
		activity_ratios = []

		U = self.massPeaks[self.uranium_peak_name]
		Th230 = self.massPeaks["ThO246"]
		Th232 = self.massPeaks["ThO248"]
		for i in range(self.numberOfScans):
			U_mean, U_stdev = U.rows[i].data[config][DataKey.BKGRD_CORRECTED]
			Th230_mean, Th230_stdev = Th230.rows[i].data[config][DataKey.BKGRD_CORRECTED]
			Th232_mean, Th232_stdev = Th232.rows[i].data[config][DataKey.BKGRD_CORRECTED]
			if U_mean <= 0:
				error_peak = U
			elif Th232_mean <= 0:
				error_peak = Th232
			elif Th230_mean <= 0:
				error_peak = Th230
			else:
				error_peak = None

			if error_peak is not None:
				error = f"Error! {error_peak.mpName} < background correction"
				activity_ratios.append(error)
				continue

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

			if self.uranium_peak_name in ["UO254", "U238"]:
				U238_mean = U_mean
				U238_stdev = U_stdev
			elif self.uranium_peak_name in ["UO251", "U235"]:
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

			activity_ratios.append((
				(U238_Th232_activity, U238_Th232_activity_uncertainty),
				(Th230_Th232_activity, Th230_Th232_activity_uncertainty)
			))

		self.data[config][DataKey.ACTIVITY_RATIOS] = activity_ratios

	def find_uranium_peak_name(self):
		for name in self.mpNamesNonBackground:
			if name.startswith("UO"):
				return name

		raise Exception("NO UO PEAK FOR SPOT " + self.name)

	def calculate_age_per_scan(self, config, WR_value, WR_uncertainty, standard_line, standard_line_uncertainty):
		ages = []
		activity_ratios = self.data[config][DataKey.ACTIVITY_RATIOS]

		for ratio in activity_ratios:
			if isinstance(ratio, str):
				result = ratio
			else:
				(x, dx), (y, dy) = ratio
				result = calculate_age_from_values(x, dx, y, dy, WR_value, WR_uncertainty, standard_line, standard_line_uncertainty)
			ages.append(result)

		self.data[config][DataKey.AGES] = ages

	def calculate_error_weighted_mean_and_st_dev_for_ages(self, config):
		data = [x for x in self.data[config][DataKey.AGES] if not isinstance(x, str)]
		if len(data) == 0:
			self.data[config][DataKey.WEIGHTED_AGE] = ("Error! No ages to take weighted mean from.", "")
		else:
			ages, uncertainties = zip(*data)
			age, uncertainty = calculate_error_weighted_mean_and_st_dev(ages, uncertainties)
			self.data[config][DataKey.WEIGHTED_AGE] = (age, uncertainty)

	def calculate_error_weighted_mean_and_st_dev_U_cps(self, config):
		U_mp = self.massPeaks[self.find_uranium_peak_name()]
		means_and_st_devs = [row.data[config][DataKey.OUTLIER_RES_MEAN_STDEV] for row in U_mp.rows]
		Us, uncertainties = zip(*means_and_st_devs)

		self.data[config][DataKey.U_CONCENTRATION] = calculate_error_weighted_mean_and_st_dev(Us, uncertainties)
