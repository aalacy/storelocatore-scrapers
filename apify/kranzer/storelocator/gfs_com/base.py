import csv

import requests
from lxml import html


class Response:
    def __init__(self, url=''):
        self._r = requests.get(url)
        self._tree = html.fromstring(self._r.text)

    def xpath(self, xpath_str=''):
        if xpath_str:
            return self._tree.xpath(xpath_str)
        raise Exception('No xpath specified')


class Spider:
    def write_output(self, data):
        if data:
            with open('data.csv', mode='w') as output_file:
                writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
                fields = ["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"]
                writer = csv.DictWriter(output_file, fieldnames=fields)
                writer.writeheader()
                for row in data:
                    writer.writerow(row.as_dict())

    def run(self):
        data = self.crawl()
        self.write_output(data)


def get_first(lst):
    lst = lst or []
    return lst[0] if len(lst) > 0 else None


class Item:
    def __init__(self, selector):
        self.locator_domain = "<MISSING>"
        self.location_name = "<MISSING>"
        self.street_address = "<MISSING>"
        self.city = "<MISSING>"
        self.state = "<MISSING>"
        self.zip = "<MISSING>"
        self.country_code = "<MISSING>"
        self.store_number = "<MISSING>"
        self.phone = "<MISSING>"
        self.location_type = "<MISSING>"
        self.latitude = "<MISSING>"
        self.longitude = "<MISSING>"
        self.hours_of_operation = "<MISSING>"
        self._tree = selector

    def add_xpath(self, attr, xpath, *processors):
        if hasattr(self, attr):
            processors = processors or []
            result = self._tree.xpath(xpath)
            for p in processors:
                result = p(result)
            setattr(self, attr, result)
        else:
            raise Exception("No such attribute \"{}\"".format(attr))

    def add_value(self, attr, value, *processors):
        if hasattr(self, attr):
            processors = processors or []
            result = value
            for p in processors:
                result = p(result)
            setattr(self, attr, result)
        else:
            raise Exception("No such attribute \"{}\"".format(attr))

    def as_dict(self):
        return {
            "locator_domain": self.locator_domain,
            "location_name": self.location_name,
            "street_address": self.street_address,
            "city": self.city,
            "state": self.state,
            "zip": self.zip,
            "country_code": self.country_code,
            "store_number": self.store_number,
            "phone": self.phone,
            "location_type": self.location_type,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "hours_of_operation": self.hours_of_operation
        }

    def __repr__(self):
        return self.as_dict()

    def __str__(self):
        return str(self.as_dict())


