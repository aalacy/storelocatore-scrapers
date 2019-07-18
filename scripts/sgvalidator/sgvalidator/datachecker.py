import pandas as pd
from .fillratechecker import FillRateChecker
from .trashvaluechecker import TrashValueChecker
from .countrychecker import CountryChecker
from .schemachecker import SchemaChecker
from .duplicationchecker import DuplicationChecker


class DataChecker:
    def __init__(self, data, debug):
        self.rawData = data
        self.data = pd.DataFrame(data)
        self.debug = debug

    def check_data(self):
        DuplicationChecker(self.data, self.debug).check()
        SchemaChecker(self.data, self.rawData, self.debug).check()  # todo - move this off of raw data
        CountryChecker(self.data, self.debug).check()
        TrashValueChecker(self.data, self.debug).check()
        FillRateChecker(self.data).check()
