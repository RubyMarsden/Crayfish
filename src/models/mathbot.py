import numpy as np
from scipy.stats import poisson
from astropy.stats import biweight_location, biweight_scale
import robustats
from sklearn.linear_model import LinearRegression
import math


def calculateOutlierResistantMeanAndStDev(row, numberOfOutliersAllowed):
	medcouple = robustats.medcouple(row)
	Q1 = np.percentile(row, 25, interpolation='midpoint')
	Q3 = np.percentile(row, 75, interpolation='midpoint')
	IQR = Q3 - Q1

	if medcouple > 0:
		lower_constant = -4
		upper_constant = 3

	else:
		lower_constant = -3
		upper_constant = 4

	skew_corrected_outlier_range = (Q1 - 1.5 * math.exp(lower_constant * medcouple) * IQR, Q3 + 1.5 * math.exp(upper_constant * medcouple) * IQR)

	# TODO add a while number of outliers is <= numberOfOutliersAllowed? how could this work?
	outliers_removed = []
	for i in row:
		if skew_corrected_outlier_range[0] < i < skew_corrected_outlier_range[1]:
			outliers_removed.append(i)

	if len(outliers_removed) < len(row) - numberOfOutliersAllowed:
		data = row

	else:
		data = outliers_removed

	return np.mean(data), np.std(data)


def calculateErrorWeightedMeanAndStDev(values, errors):
    inverseErrors = [1 / (error ** 2) for error in errors]
    sigma = sum(inverseErrors)
    weightedMean = (sum([value * inverseError for value, inverseError in zip(values, inverseErrors)])) / sigma
    weightedStDev = math.sqrt(1 / sigma)
    return weightedMean, weightedStDev


def calculateRelativeErrors(value, absoluteError):
    if value != 0:
        return absoluteError / value
    else:
        return 0


def errors_in_quadrature(errors):
    return math.sqrt(sum([error ** 2 for error in errors]))


def estimateExponential(point1, error1, point2, error2, x):
    x1, y1 = point1
    x2, y2 = point2
    assert y2 < y1
    # if there is no additional background from the previous peak then we should use the second background as it is
    # what is used for all other peaks and it should be random and so doesn't matter where you take it.

    # for an exponential curve y = a*exp(bx)
    if y2 == 0:
        y2 = 0.000001
    b = math.log(y2 / y1) / (x2 - x1)
    a = y1 * (math.exp(-b * x1))

    dfdy1 = (math.exp(b * x) / (x1 - x2)) * (((a * x) / y1) - (math.exp(-b * x1) * x2))
    dfdy2 = (math.exp(b * x) / (y2 * (x2 - x1))) * ((a * x) - ((math.exp(-b * x1)) * y1 * x1))

    yEstimatedBackgroundError = math.sqrt((error1 * dfdy1) ** 2 + (error2 * dfdy2) ** 2)
    yEstimatedBackground = a * (math.exp(b * x))

    return a, b, yEstimatedBackground, yEstimatedBackgroundError


def activityRatio(cpsMass1, cpsMass1Error, decayC1, decayC1Error, cpsMass2, cpsMass2Error, decayC2, decayC2Error):
    # is there a way to make sure that Th232 goes on the bottom?
    activityRatio = (cpsMass1 * decayC1) / (cpsMass2 * decayC2)
    activityRatioError = activityRatio * (math.sqrt(
        ((cpsMass1Error / cpsMass1) ** 2) + ((cpsMass2Error / cpsMass2) ** 2) + ((decayC1Error / decayC1) ** 2) + (
                    (decayC2Error / decayC2) ** 2)))
    return activityRatio, activityRatioError


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
