import unittest

from models import settings
from models.mathbot import *
from models.settings import U238_DECAY_CONSTANT, U238_DECAY_CONSTANT_ERROR, TH232_DECAY_CONSTANT, \
    TH232_DECAY_CONSTANT_ERROR


class MathbotTests(unittest.TestCase):

    ########################################
    ### Outlier resistant mean and stdev ###
    ########################################

    def test_outlier_resistant_mean_no_outliers_allowed(self):
        test_data = [1, 1, 2, 1, 4, 1, 2, 3, 9, 2]
        mean, st_dev = calculate_outlier_resistant_mean_and_st_dev(test_data, 0)
        self.assertEqual(np.mean(test_data), mean)
        self.assertEqual(np.std(test_data), st_dev)

    def test_outlier_resistant_mean_zeros(self):
        test_data = [0] * 10
        self.assertEqual((0, 0), calculate_outlier_resistant_mean_and_st_dev(test_data, 2))

    def test_outlier_resistant_mean_empty_set(self):
        self.assertRaises(IndexError, calculate_outlier_resistant_mean_and_st_dev, [], 2)

    def test_outlier_resistant_mean_one_higher_outlier(self):
        test_data = [1, 1, 1, 1, 1, 1, 1, 1, 1, 40]
        mean, st_dev = calculate_outlier_resistant_mean_and_st_dev(test_data, 1)
        mean_2, st_dev_2 = calculate_outlier_resistant_mean_and_st_dev(test_data, 2)
        self.assertEqual(1, mean)
        self.assertEqual(0, st_dev)
        self.assertEqual(1, mean_2)
        self.assertEqual(0, st_dev_2)

    def test_outlier_resistant_mean_one_lower_outlier(self):
        test_data = [1, 40, 40, 40, 40, 40, 40, 40, 40, 40]
        mean, st_dev = calculate_outlier_resistant_mean_and_st_dev(test_data, 1)
        mean_2, st_dev_2 = calculate_outlier_resistant_mean_and_st_dev(test_data, 2)
        self.assertEqual(40, mean)
        self.assertEqual(0, st_dev)
        self.assertEqual(40, mean_2)
        self.assertEqual(0, st_dev_2)

    def test_outlier_resistant_mean_two_outliers(self):
        test_data = [1, 40, 40, 40, 40, 40, 40, 40, 40, 400]
        mean, st_dev = calculate_outlier_resistant_mean_and_st_dev(test_data, 1)
        mean_2, st_dev_2 = calculate_outlier_resistant_mean_and_st_dev(test_data, 2)
        self.assertEqual(np.mean(test_data), mean)
        self.assertEqual(np.std(test_data), st_dev)
        self.assertEqual(40, mean_2)
        self.assertEqual(0, st_dev_2)

    #######################
    ### Relative errors ###
    #######################

    def test_relative_errors_zero_case(self):
        self.assertEqual(0, relative_error(0, 4))

    def test_relative_errors_general(self):
        self.assertEqual(0.1, relative_error(10, 1))

    ############################
    ### Errors in quadrature ###
    ############################

    def test_errors_in_quadrature_single_error(self):
        self.assertEqual(1, errors_in_quadrature([1]))

    def test_errors_in_quadrature_general(self):
        self.assertEqual(13, errors_in_quadrature([5, 12]))

    def test_errors_in_quadrature_negative(self):
        self.assertEqual(13, errors_in_quadrature([-5, 12]))

    def test_errors_in_quadrature_decimals(self):
        self.assertEqual(0.2, errors_in_quadrature([0.1, 0.1, 0.1, 0.1]))

    ########################################
    ### Interpolate to exponential curve ###
    ########################################

    def test_interpolate_to_exponential(self):
        a, b, y_est_rounded, y_est_rounded_uncertainty = interpolate_to_exponential((0, 10), 3, (1, 5), 2, 0.5)
        self.assertEqual(10, a)
        self.assertAlmostEqual(-0.693147180559945, b, 14)
        self.assertAlmostEqual(7.07106781186548, y_est_rounded, 14)
        self.assertAlmostEqual(1.76776695296637, y_est_rounded_uncertainty, 14)

    def test_interpolate_to_exponential_invalid_points(self):
        self.assertRaises(AssertionError, interpolate_to_exponential, (0, 0), 0, (0, 0), 0, 0)
        self.assertRaises(AssertionError, interpolate_to_exponential, (0, 10), 0, (1, 5), 0, 2)

    ######################
    ### Activity ratio ###
    ######################

    def test_activity_ratio_general(self):
        ratio, ratio_uncertainty = activity_ratio(
            cps_mass_1=10,
            cps_mass_1_uncertainty=1,
            decay_constant_1=2,
            decay_constant_1_uncertainty=0.2,
            cps_mass_2=20,
            cps_mass_2_uncertainty=2,
            decay_constant_2=5,
            decay_constant_2_uncertainty=0.5
        )

        self.assertEqual(0.2, ratio)
        self.assertAlmostEqual(0.04, ratio_uncertainty, 16)

    def test_activity_ratio_data_values(self):
        # using data from Heidelberg University 05/2020

        ratio, ratio_uncertainty = activity_ratio(
            cps_mass_1=12.0540007,
            cps_mass_1_uncertainty=0.01,
            decay_constant_1=U238_DECAY_CONSTANT,
            decay_constant_1_uncertainty=U238_DECAY_CONSTANT_ERROR,
            cps_mass_2=10,
            cps_mass_2_uncertainty=0.01,
            decay_constant_2=TH232_DECAY_CONSTANT,
            decay_constant_2_uncertainty=TH232_DECAY_CONSTANT_ERROR
        )

        self.assertAlmostEqual(3.77943781422436, ratio, 14)
        self.assertAlmostEqual(0.00531355971346501, ratio_uncertainty, 14)

    def test_activity_ratio_invalid_input(self):
        self.assertRaises(AssertionError, activity_ratio,
                          cps_mass_1=-1,
                          cps_mass_1_uncertainty=0.01,
                          decay_constant_1=U238_DECAY_CONSTANT,
                          decay_constant_1_uncertainty=U238_DECAY_CONSTANT_ERROR,
                          cps_mass_2=10,
                          cps_mass_2_uncertainty=0.01,
                          decay_constant_2=TH232_DECAY_CONSTANT,
                          decay_constant_2_uncertainty=TH232_DECAY_CONSTANT_ERROR
                          )

    #########################
    ### Age from gradient ###
    #########################

    def test_age_from_gradient_zero_uncertainty(self):
        age, uncertainty = calculate_age_from_values(0.5, 0, 1, 0, 0, 0)
        self.assertEqual(-math.log(0.5) / settings.TH230_DECAY_CONSTANT, age)
        self.assertEqual(uncertainty, 0)

    def test_age_from_gradient_more_realistic(self):
        age, uncertainty = calculate_age_from_values(3.02, 0.05, 6.33, 0.16, 0.32, 0.01)
        self.assertEqual(-math.log(1 - (3.02 - 0.32)/(6.33 - 0.32)) / settings.TH230_DECAY_CONSTANT, age)
        self.assertAlmostEqual(2459.439109, uncertainty, 6)


if __name__ == '__main__':
    unittest.main()
