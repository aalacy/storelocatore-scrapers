from unittest import TestCase
from ..trash_value_checker import TrashValueChecker


def getExampleRow():
    return {
        "locator_domain": "example.com",
        "location_name": "Bob's Trucks",
        "street_address": "1543 Mission",
        "city": "Dallas",
        "state": "Texas",
        "zip": "75230",
        "country_code": "us",
        "store_number": "123",
        "phone": "2149260428",
        "location_type": "ATM",
        "latitude": "38.12312",
        "longitude": "-59.1231",
        "hours_of_operation": "24/7"
    }


class TestTrashValueChecker(TestCase):
    def testFindTrashValues(self):
        exampleRowGood = getExampleRow()

        exampleRowBad1 = getExampleRow()
        exampleRowBad1["store_number"] = exampleRowBad1["store_number"] + " null"
        exampleRowBad1["longitude"] = "<MISSING>"

        exampleRowBad2 = getExampleRow()
        exampleRowBad2["phone"] = exampleRowBad2["phone"] + " <span>"
        exampleRowBad2["longitude"] = "null " + exampleRowBad2["longitude"]
        exampleRowBad2["zip"] = "null"

        self.assertFalse(TrashValueChecker.findTrashValuesInner(exampleRowGood))
        self.assertTrue(TrashValueChecker.findTrashValuesInner(exampleRowBad1))
        self.assertTrue(TrashValueChecker.findTrashValuesInner(exampleRowBad2))
