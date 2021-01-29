import unittest
import numpy as np
import matplotlib.pyplot as plt
from models.york_regression import bivariate_fit


class YorkRegressionTests(unittest.TestCase):
    def test_york_regression_invalid_inputs(self):
        xs = [0, 0, 0, "hi"]
        ys = [0, 0, 0, 0]
        dxs = [0, 0, 0, 0]
        dys = [0, 0, 0, 0]
        self.assertRaises(Exception, bivariate_fit, xs, ys, dxs, dys)

    def test_york_regression_one_point(self):
        xs = np.array([0])
        ys = np.array([0])
        dxs = np.array([0])
        dys = np.array([0])
        a, b, S, cov_matrix = bivariate_fit(xs, ys, dxs, dys)
        # TODO fix this so it tells you that there's only one point
        # self.assertRaises(Exception, bivariate_fit, xs, ys, dxs, dys)

    def test_york_regression_xs_and_ys_different_length(self):
        xs = np.array([0, 1, 2])
        ys = np.array([0, 1, 2, 3])
        dxs = np.array([0.5, 1, 2])
        dys = np.array([0.5, 1, 2])
        # a, b, S, cov_matrix = bivariate_fit(xs, ys, dxs, dys)
        self.assertRaises(Exception, bivariate_fit, xs, ys, dxs, dys)

    def test_york_regression_zero_errors(self):
        xs = np.array([1, 2, 3])
        ys = np.array([1, 2, 3])
        dxs = np.array([0, 0.1, 0.2])
        dys = np.array([0, 0.1, 0.2])
        self.assertRaises(Exception, bivariate_fit, xs, ys, dxs, dys)

    def test_york_regression_data_checked_isoplot_MSWD_0(self):
        xs = np.array([i for i in range(1,10)])
        ys = np.array([i/10 for i in range(9, 90, 9)])
        dxs = xs/20
        dys = ys/20
        a, b, S, cov_matrix = bivariate_fit(xs, ys, dxs, dys)
        self.assertAlmostEqual(0, a, 15)
        self.assertAlmostEqual(0.9, b, 15)
        self.assertAlmostEqual(0, S)
        # self.assertAlmostEqual(0.003481, cov_matrix[0][0])
        # self.assertAlmostEqual(0.0225, cov_matrix[1][1])


    def test_york_regression_from_retrieval(self):
        """
        Test the Yorks bivariate line fitting by attempting linear fit similarly as in Fig. 1 in Cantrell et al, 2008,
        Technical Note: Review of methods for linear least-squares fitting of data and application to atmospheric
        chemistry problems, Atmos. Chem. Phys., doi 10.5194/acp-8-5477-2008
        In Ipython you can use this test by calling:
        run bivariate_fit.py
        """

        fig1 = plt.figure(1)
        ax1 = fig1.add_subplot(111)

        # define test data set points
        x = np.array([0.0, 0.9, 1.8, 2.6, 3.3, 4.4, 5.2, 6.1, 6.5, 7.4])
        y = np.array([5.9, 5.4, 4.4, 4.6, 3.5, 3.7, 2.8, 2.8, 2.4, 1.5])

        # define weights for the data points
        wx = np.array(
            [1000.0, 1000.0, 500.0, 800.0, 200.0, 80.0, 60.0, 20.0, 1.8, 1.0])
        wy = np.array([1.0, 1.8, 4.0, 8.0, 20.0, 20.0, 70.0, 70.0, 100.0, 500.0])

        # plot error bar
        ax1.errorbar(x, y, xerr=1 / (wx ** 0.5), yerr=1 / (wy ** 0.5), fmt='o')

        # remember to convert weights to errors by 1/wx**0.5
        a_bivar, b_bivar, S, cov = bivariate_fit(
            x, y, 1 / (wx ** 0.5), 1 / (wy ** 0.5), b0=0.0)
        label_bivar = 'y={:1.2f}x+{:1.2f}'.format(b_bivar, a_bivar)

        a_ols = np.polyfit(x, y, 1)
        label_ols = 'y={:1.2f}x+{:1.2f}'.format(a_ols[0], a_ols[1])

        xlim = np.array([-0.5, 8.5])
        ylim = np.array([0, 8])

        ax_york = plt.plot(xlim, b_bivar * xlim + a_bivar, 'b-',
                           label='York et al, 2004: ' + label_bivar)

        ax_lsq = plt.plot(xlim, a_ols[0] * xlim + a_ols[1], 'r-',
                          label='Standard OLS, no weigths: ' + label_ols)

        ax1.legend()

        plt.suptitle('Cantrell et al, 2008, Fig. 1, adopted', fontsize=16)

        ax1.set_xlabel('x data')
        ax1.set_ylabel('y data')

        ax1.set_xlim(xlim)
        ax1.set_ylim(ylim)

        ax1.grid(b=True)
        plt.show()


if __name__ == '__main__':
    unittest.main()
