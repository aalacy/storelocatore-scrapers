import termcolor
from .validator_utils import ValidatorUtils
from .abstract_checker import AbstractChecker


class DuplicationChecker(AbstractChecker):
    def __init__(self, data, debug):
        self.data = data
        self.debug = debug
        self.keys = ["street_address", "city", "state", "zip", "country_code", "location_type"]

    def check(self):
        print(termcolor.colored("Checking for duplicate rows in the data...", "blue"))
        duplicateRows = DuplicationChecker.getDuplicateRows(self.data, self.keys)
        debugExamples = duplicateRows[self.keys].head(10)
        if len(debugExamples) > 0:
            ValidatorUtils.fail("Found {} duplicate keys in data. Examples: \n {}"
                                .format(len(duplicateRows), debugExamples), self.debug)
        if len(debugExamples) == 0:
            print(termcolor.colored("No duplicates found...", "green"))

    @staticmethod
    def getDuplicateRows(df, keys):
        return df[df.duplicated(subset=keys)]