import matplotlib.pyplot as plt
from shrimp_spot import *
import numpy as np

RESOLUTION = 20

def plotExponentialBackground(spot, onSameGraph):
	for i in range(spot.numberOfScans):
		x1 = spot.mpXValues[BACKGROUND1][i]
		x2 = spot.mpXValues[BACKGROUND2][i]
		incr = (x2 - x1)/float(RESOLUTION)
		yFunc = spot.expEstimatedBackgroundFunction[i]

		xs = np.arange(x1,x2+incr,incr)
		ys = [yFunc(x) for x in xs]

		if not onSameGraph:
			plt.subplot(420 + i + 1)
		plt.plot(xs,ys)

	plt.xlabel("Mass (AMU)")
	plt.ylabel("Intensity (counts per 20s)")
	plt.title(spot.name)
	plt.show()


def plotLine(c,m, xMin, xMax):
	incr = (xMax-xMin)/RESOLUTION
	lineXs = np.arange(xMin,xMax+incr,incr)
	lineYs = [m*x+c for x in lineXs]

	plt.plot(lineXs, lineYs)


def plotLinearRegressionWithData (name,xs,ys,xErrors,yErrors,c,m):
	xMax = max(xs)
	incr = xMax/RESOLUTION
	lineXs = np.arange(0,xMax+incr,incr)
	lineYs = [m*x+c for x in lineXs]

	plt.errorbar(xs,ys,xerr=xErrors,yerr=yErrors,fmt="none")
	plt.plot(lineXs, lineYs)
	plt.title(name+" m="+str(round(m,3))+" c="+str(round(c,3)))


def showPlot():
	plt.show()