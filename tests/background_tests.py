import unittest

from models.mathbot import interpolate_to_exponential
from models.row import Row
from models.data_key import DataKey


class BackgroundCorrectionTest(unittest.TestCase):

    def instantiate_mass_peaks_single_data_point(self):
        background1 = Row("Test", "B1", 1, 0, [10], [1])
        background1.data["counts"] = 10, 1
        background2 = Row("Test", "B2", 1, 1 , [5], [1])
        background2.data["counts"] = 5, 0.5
        Th_peak = Row("Test", "ThO246", 1, 0.5, [9], [1])
        Th_peak.data["counts"] = 9, 0.9
        return background1, background2, Th_peak

    def test_exponential_background(self):
        background1, background2, Th_peak = self.instantiate_mass_peaks_single_data_point()
        Th_peak.exponential_correction(background1, background2, DataKey.BKGRD_CORRECTED, "counts")

        self.assertAlmostEqual(1.92893218813452, Th_peak.data[DataKey.BKGRD_CORRECTED][0], 14)

    def test_linear_background(self):
        background1, background2, Th_peak = self.instantiate_mass_peaks_single_data_point()
        Th_peak.linear_correction(background1, background2, "output_linear", "counts")

        self.assertEqual(1.5, Th_peak.data["output_linear"][0])

    def test_constant_background_all_peaks(self):
        background1, background2, Th_peak = self.instantiate_mass_peaks_single_data_point()
        background2.data[DataKey.OUTLIER_RES_MEAN_STDEV] = 5, 0.5
        background2.data[DataKey.OUTLIER_RES_MEAN_STDEV_SBM] = 5, 0.5
        Th_peak.data[DataKey.OUTLIER_RES_MEAN_STDEV] = 9, 0.9
        Th_peak.data[DataKey.OUTLIER_RES_MEAN_STDEV_SBM] = 9, 0.9
        Th_peak.constant_background_correction(background2)

        self.assertEqual(4, Th_peak.data[DataKey.BKGRD_CORRECTED][0])
        self.assertEqual(4, Th_peak.data[DataKey.BKGRD_CORRECTED_SBM][0])


if __name__ == '__main__':
    unittest.main()
