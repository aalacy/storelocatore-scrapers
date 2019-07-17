import termcolor
from .datachecker import DataChecker


def validate(data, debug):
    print(termcolor.colored("Validating data...", "green"))
    checks = DataChecker(data, debug)
    checks.check_data()
