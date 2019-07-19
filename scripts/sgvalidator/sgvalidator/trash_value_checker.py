import termcolor
from .validator_utils import ValidatorUtils
from .abstract_checker import AbstractChecker

class TrashValueChecker(AbstractChecker):
    """
    Checks for trash values in the data, like "null" or HTML tags, both when they're
    standalone and also when they're mixed with other data, e.g. "Bob's Burgers null"

    Filters to values that have some or all of BAD_TOKENS_INCLUDE but which do NOT include
    anything from BAD_TOKENS_EXCLUDE
    """
    BAD_TOKENS_INCLUDE = ["null", "<", ">"]
    BAD_TOKENS_EXCLUDE = ["<MISSING>", "<INACCESSIBLE>"]

    def __init__(self, data, debug):
        self.data = data
        self.debug = debug

    def check(self):
        res = TrashValueChecker.findTrashValues(self.data)
        debugExamples = res.head(10)
        if len(res) > 0:
            ValidatorUtils.fail("Found {} rows with trash data (e.g. nulls, HTML tags, etc.). Examples:\n{}\n"
                                .format(len(res), debugExamples), self.debug)
        else:
            print(termcolor.colored("No trash values found...", "green"))

    @staticmethod
    def findTrashValues(data):
        mask = data.apply(TrashValueChecker.findTrashValuesInner, axis=1)
        return data[mask]

    @staticmethod
    def findTrashValuesInner(row):
        for key, value, in row.items():
            badTokensIncludeFilter = set(filter(lambda x: x in value, TrashValueChecker.BAD_TOKENS_INCLUDE))
            badTokensExcludeFilter = set(filter(lambda x: x in value, TrashValueChecker.BAD_TOKENS_EXCLUDE))
            if len(badTokensIncludeFilter) > 0 and len(badTokensExcludeFilter) == 0:
                return True
        return False
