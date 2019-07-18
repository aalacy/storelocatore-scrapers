import termcolor
from .validatorutils import ValidatorUtils


class DuplicationChecker:
    def __init__(self, data, debug):
        self.data = data
        self.debug = debug

    def check(self):
        print(termcolor.colored("Checking for duplicate rows in the data...", "blue"))
        keys = ["street_address", "city", "state", "zip", "country_code", "location_type"]
        duplicateRows = self.data[self.data.duplicated(subset=keys)]
        debugExamples = duplicateRows[keys].head(10)
        if len(debugExamples) > 0:
            ValidatorUtils.fail("Found {} duplicate keys in data. Examples: \n {}"
                                .format(len(duplicateRows), debugExamples), self.debug)
        if len(debugExamples) == 0:
            print(termcolor.colored("No duplicates found...", "green"))