import unittest
from models.mathbot import calculateOutlierResistantMeanAndStDev
from models.row import Row, DataKey
import robustats

class DataReductionTest(unittest.Testcase):

    def test_outlier_resistant_mean(self):
        row = Row("Test", "B1", 1, 0, [10], [1])
        # TODO fix this
        row.data["test"] = [1, 1, 2, 1, 4, 1, 2, 3, 9, 2]
        print(robustats.medcouple(row.data["test"]))
        self.assertEqual((2.6,calculateOutlierResistantMeanAndStDev(row.data["test"], 0)[0])

        #calculateOutlierResistantMeanAndStDev(row.data["test"], 1)


if __name__ == '__main__':
    unittest.main()
