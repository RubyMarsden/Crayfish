from enum import Enum


class BackgroundCorrection(Enum):
    EXP = "Exponential"
    LIN = "Linear"
    CONST = "Constant"
    NONE = "None"
