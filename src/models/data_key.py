from enum import Enum


class DataKey(Enum):
    ### ROW ###
    COUNTS = "raw counts"
    SBM_COUNTS = "raw sbm counts"
    SBM_CPS_STANDARDISED = "sbm cps standardised"
    CPS = "counts per second"
    OUTLIER_RES_MEAN_STDEV = "outlier resistant mean and st deviation for cps values"
    BKGRD_CORRECTED = "background correction applied to outlier resistant mean and st deviation for cps values"

    ### SPOT ###
    ACTIVITY_RATIOS = "activity ratios"
    WEIGHTED_ACTIVITY_RATIO = "weighted activity ratio"
    AGES = "ages"
    WEIGHTED_AGE = "weighted age"
    U_CONCENTRATION = "weighted U cps"

    ### MODEL ###
    STANDARD_LINE_GRADIENT = "standard line"
    STANDARD_LINE_MSWD = "standard line MSWD"

