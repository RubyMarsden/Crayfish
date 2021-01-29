import numpy as np
# from scipy.stats import poisson
# from astropy.stats import biweight_location, biweight_scale
import statsmodels.stats.stattools as stattools
# import robustats
from sklearn.linear_model import LinearRegression
import math


def calculate_outlier_resistant_mean_and_st_dev(data, number_of_outliers_allowed):
    medcouple = stattools.medcouple(data)
    Q1 = np.percentile(data, 25, interpolation='midpoint')
    Q3 = np.percentile(data, 75, interpolation='midpoint')
    IQR = Q3 - Q1

    if medcouple > 0:
        lower_constant = -4
        upper_constant = 3
    else:
        lower_constant = -3
        upper_constant = 4

    skew_corrected_outlier_minimum = Q1 - 1.5 * math.exp(lower_constant * medcouple) * IQR
    skew_corrected_outlier_maximum = Q3 + 1.5 * math.exp(upper_constant * medcouple) * IQR

    data_without_outliers = []
    for x in data:
        if skew_corrected_outlier_minimum <= x <= skew_corrected_outlier_maximum:
            data_without_outliers.append(x)

    if len(data_without_outliers) < len(data) - number_of_outliers_allowed:
        clean_data = data
    else:
        clean_data = data_without_outliers

    return np.mean(clean_data), np.std(clean_data)

def relative_error(value, absolute_error):
    if value == 0:
        return 0
    return absolute_error / value


def errors_in_quadrature(errors):
    return math.sqrt(sum([error ** 2 for error in errors]))


def interpolate_to_exponential(point1, error1, point2, error2, x):
    x1, y1 = point1
    x2, y2 = point2
    assert x1 < x < x2
    assert y2 < y1

    # for an exponential curve y = a*exp(bx)
    if y2 == 0:
        y2 = 0.000001
    b = math.log(y2 / y1) / (x2 - x1)
    a = y1 * (math.exp(-b * x1))

    dfdy1 = (math.exp(b * x) / (x1 - x2)) * (((a * x) / y1) - (math.exp(-b * x1) * x2))
    dfdy2 = (math.exp(b * x) / (y2 * (x2 - x1))) * ((a * x) - ((math.exp(-b * x1)) * y1 * x1))

    yEstimatedBackgroundError = errors_in_quadrature([error1 * dfdy1, error2 * dfdy2])
    yEstimatedBackground = a * math.exp(b * x)

    return a, b, yEstimatedBackground, yEstimatedBackgroundError


def activity_ratio(cps_mass_1, cps_mass_1_uncertainty,
                   decay_constant_1, decay_constant_1_uncertainty,
                   cps_mass_2, cps_mass_2_uncertainty,
                   decay_constant_2, decay_constant_2_uncertainty):
    assert cps_mass_1 > 0
    assert cps_mass_1_uncertainty >= 0
    assert cps_mass_2 > 0
    assert cps_mass_2_uncertainty >= 0

    ratio = (cps_mass_1 * decay_constant_1) / (cps_mass_2 * decay_constant_2)
    ratio_uncertainty = ratio * errors_in_quadrature([
        relative_error(cps_mass_1, cps_mass_1_uncertainty),
        relative_error(cps_mass_2, cps_mass_2_uncertainty),
        relative_error(decay_constant_1, decay_constant_1_uncertainty),
        relative_error(decay_constant_2, decay_constant_2_uncertainty)
    ])
    return ratio, ratio_uncertainty


# NOT YORK REGRESSION *sigh*
def weightedRegression(xs, ys, xErrors, yErrors, fitIntercept):
    weights = [1 / math.sqrt(xE ** 2 + yE ** 2) for xE, yE in zip(xErrors, yErrors)]
    xs = np.array(xs).reshape(-1, 1)
    model = LinearRegression(fit_intercept=fitIntercept)
    model.fit(xs, ys, sample_weight=weights)
    return model.intercept_, model.coef_


def ageFromGradient(m, decayC):
    if 1 - m > 0:
        age = -math.log(1 - m) / decayC
        return age
    else:
        return 0

def calculateErrorWeightedMeanAndStDev(values, errors):
    inverseErrors = [1 / (error ** 2) for error in errors]
    sigma = sum(inverseErrors)
    weightedMean = (sum([value * inverseError for value, inverseError in zip(values, inverseErrors)])) / sigma
    weightedStDev = math.sqrt(1 / sigma)
    return weightedMean, weightedStDev