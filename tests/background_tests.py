import unittest

from models.mathbot import estimateExponential
from models.row import Row
# from models.row import linear_correction, constant_correction, exponential_correction


class BackgroundCorrectionTest(unittest.TestCase):

    def test_math_exponential(self):
        a, b, y_est_rounded = estimateExponential((0, 10), (1, 5), 0.5)
        self.assertAlmostEqual(7.07, y_est_rounded, 1)

    def instantiate_mass_peaks_single_data_point(self):
        background1 = Row("Test", "B1", 1, 0, [10], [1])
        background1.data["counts"] = [10]
        background2 = Row("Test", "B2", 1, 1 , [5], [1])
        background2.data["counts"] = [5]
        Th_peak = Row("Test", "ThO246", 1, 0.5, [9], [1])
        Th_peak.data["counts"] = [9]
        return background1, background2, Th_peak

    def test_exponential_background(self):
        background1, background2, Th_peak = self.instantiate_mass_peaks_single_data_point()
        Th_peak.exponential_correction(background1, background2, "output_exp", "counts")

        self.assertAlmostEqual(1.93, Th_peak.data["output_exp"][0], 1)

    def test_linear_background(self):
        background1, background2, Th_peak = self.instantiate_mass_peaks_single_data_point()
        Th_peak.linear_correction(background1, background2, "output_linear", "counts")

        self.assertEqual(1.5, Th_peak.data["output_linear"][0])

    def test_constant_background_230(self):
        background1, background2, Th_peak = self.instantiate_mass_peaks_single_data_point()
        Th_peak.constant_correction(background2, "output_constant", "counts")

        self.assertEqual(4, Th_peak.data["output_constant"][0])

    def test_constant_background_all_peaks(self):
        background1, background2, Th_peak = self.instantiate_mass_peaks_single_data_point()
        background2.data["counts normalised to time"] = [5]
        background2.data["peak cps normalised by sbm"] = [5]
        Th_peak.data["counts normalised to time"] = [9]
        Th_peak.data["peak cps normalised by sbm"] = [9]
        Th_peak.background_correction_all_peaks(background2)

        self.assertEqual(4, Th_peak.data["background corrected all peaks"][0])
        self.assertEqual(4, Th_peak.data["sbm normalised background corrected all peaks"][0])

if __name__ == '__main__':
    unittest.main()