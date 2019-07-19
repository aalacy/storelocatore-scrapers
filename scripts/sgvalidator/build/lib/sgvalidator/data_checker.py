import pandas as pd
from .fill_rate_checker import FillRateChecker
from .trash_value_checker import TrashValueChecker
from .country_checker import CountryChecker
from .schema_checker import SchemaChecker
from .duplication_checker import DuplicationChecker


class DataChecker:
    def __init__(self, data, debug):
        self.rawData = data
        self.data = pd.DataFrame(data)
        self.debug = debug
        self.checkers = {
            SchemaChecker(self.data, self.rawData, self.debug),  # todo - move this off of raw data
            DuplicationChecker(self.data, self.debug),
            CountryChecker(self.data, self.debug),
            TrashValueChecker(self.data, self.debug),
            FillRateChecker(self.data)
        }

    def check_data(self):
        for checker in self.checkers:
            checker.check()
