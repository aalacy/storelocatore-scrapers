import termcolor
from collections import defaultdict


class FillRateChecker:
    """
    Checks the percentage of each columns which is null and warns if it's greater than some cutoff
    """
    PERC_CUTOFF = 40

    @staticmethod
    def checkFillRate(data):
        dataCount = len(data)
        nullCountsByColumn = defaultdict(int)
        for row in data:
            for key, value in row.items():
                if value is "" or value is None:
                    nullCountsByColumn[key] += 1

        counter = 0
        for col, nullCount in nullCountsByColumn.items():
            percNull = 100.0 * nullCount / dataCount
            if percNull > FillRateChecker.PERC_CUTOFF:
                counter += 1
                message = "{0:.2f}% of column {1} is null...are you sure you scraped correctly?".format(percNull, col)
                print(termcolor.colored(message, "yellow"))

        if counter > 0:
            print(termcolor.colored("Found {} columns with {}% nulls or more".format(counter, FillRateChecker.PERC_CUTOFF), "red"))

        # returning so that I can test
        return nullCountsByColumn
