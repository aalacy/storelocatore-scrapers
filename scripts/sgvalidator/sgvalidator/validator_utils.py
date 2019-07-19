import phonenumbers
import termcolor


class ValidatorUtils:
    @staticmethod
    def fail(message, debug=True):
        if debug:
            print(termcolor.colored(message, "red"))
        else:
            raise AssertionError(termcolor.colored(message, "red"))

    @staticmethod
    def is_number(s):
        try:
            float(s)
            return True
        except ValueError:
            return False

    @staticmethod
    def is_valid_phone_number(phone, country):
        try:
            return phonenumbers.is_possible_number(phonenumbers.parse(phone, country))
        except:
            return False

    @staticmethod
    def is_blank(field):
        if field in ['<MISSING>', '<INACCESSIBLE>']:
            return True
        return not bool(field)
