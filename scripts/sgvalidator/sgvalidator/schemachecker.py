import termcolor
from .validatorutils import ValidatorUtils


class SchemaChecker:
    def __init__(self, data, rawData, debug):
        self.data = data
        self.rawData = rawData
        self.debug = debug
        self.requiredColumns = {"locator_domain", "location_name", "street_address", "city", "state", "zip",
                                "country_code", "store_number", "phone", "location_type", "latitude", "longitude",
                                "hours_of_operation"}

    def check(self):
        print(termcolor.colored("Validating output schema...", "blue"))
        requiredColsNotInData = self.requiredColumns.difference(self.data.columns)
        if len(requiredColsNotInData) > 0:
            ValidatorUtils.fail("Data does not contain the following required columns {}"
                                .format(requiredColsNotInData), self.debug)

        # todo - transition to pandas somehow (right now pandas has dtype as object for everything)...
        for row in self.rawData:
            for column in row:
                if type(row[column]) not in [type(None), type(''), type(u''), type(0), type(0.0), type(True)]:
                    ValidatorUtils.fail("row {} contains unexpected data type {}".format(row, type(row[column])),
                                        self.debug)

        if len(requiredColsNotInData) == 0:
            print(termcolor.colored("Output schema looks good!", "green"))