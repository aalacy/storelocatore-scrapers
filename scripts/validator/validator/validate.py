from .checks import *


def validate(data, debug):
    check_schema(data, debug)
    check_values(data, debug)
    check_duplication(data, debug)
