import unittest

from models.mathbot import estimateExponential
from models.row import linear_correction, constant_correction, exponential_correction


class BackgroundCorrectionTest(unittest.TestCase):

    def math_exponential_test(self):
        y_est_rounded = round(estimateExponential((0, 10), (1, 5), 0.5), 1)

        self.assertTrue(y_est_rounded == 0.7)
        self.assertFalse(estimateExponential(0,5), (1,10), 0.5)

    def exponential_background_test(self):
        background1 =
        background2 =
        230Th_peak = 

if __name__ == '__main__':
    unittest.main()