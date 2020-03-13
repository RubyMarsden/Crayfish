
class Configuration:
	def __init__(self,
                 normaliseBySBM,
                 exponential_background_correction,
                 sample_prefixes,
                 standard_prefixes,
                 input_file,
                 row_output_file,
                 age_output_file):
		self.normaliseBySBM = normaliseBySBM
		self.exponential_background_correction = exponential_background_correction
		self.sample_prefixes = sample_prefixes
		self.standard_prefixes = standard_prefixes
		self.input_file = input_file
		self.row_output_file = row_output_file
		self.age_output_file = age_output_file

