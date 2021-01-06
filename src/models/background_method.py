from enum import Enum


class BackgroundCorrection(Enum):
    EXP = "Exponential"
    LIN = "Linear"
    CONST = "No further 230Th background correction"
