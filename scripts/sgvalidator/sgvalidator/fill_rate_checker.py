import termcolor
from .abstract_checker import AbstractChecker


class FillRateChecker(AbstractChecker):
    """
    Checks the percentage of each columns which is null or blank and warns if it's greater than some cutoff.
    To add a new fill rate check, just define a boolean mask and pass to `checkFillRateInner`
    """
    PERC_CUTOFF = 40

    def __init__(self, data):
        self.data = data

    def check(self):
        percNullDf = self.data.isna().mean() * 100
        percBlankDf = self.data.apply(lambda x: x == "", axis=0).mean() * 100
        FillRateChecker.checkInner(percNullDf, "null")
        FillRateChecker.checkInner(percBlankDf, "blanks")

    @staticmethod
    def checkInner(mask, desc):
        concerningColsWithPercentages = mask[mask > FillRateChecker.PERC_CUTOFF]
        if len(concerningColsWithPercentages) > 0:
            message = "WARNING: {} columns have a high percentage (> {}%) of {}. " \
                      "Are you sure you scraped correctly?\n{}\n"\
                .format(len(concerningColsWithPercentages), FillRateChecker.PERC_CUTOFF, desc,
                        concerningColsWithPercentages)
            print(termcolor.colored(message, "yellow"))
        return concerningColsWithPercentages
