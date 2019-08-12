import csv

import requests
from lxml import html


class Response:
    def __init__(self, url=''):
        self._r = requests.get(url)
        self._tree = html.fromstring(self._r.text)

    def xpath(self, xpath_str=''):
        if xpath_str:
            return self._tree.xpath(xpath_str) or '<MISSING>'
        raise Exception('No xpath specified')


us_states = ['alabama', 'alaska', 'arizona', 'arkansas', 'california', 'colorado', 'connecticut', 'delaware', 'florida', 'georgia', 'hawaii', 'idaho', 'illinois', 'indiana', 'iowa', 'kansas', 'kentucky', 'louisiana', 'maine', 'maryland', 'massachusetts', 'michigan', 'minnesota', 'mississippi', 'missouri', 'montana', 'nebraska', 'nevada', 'new hampshire', 'new jersey', 'new mexico', 'new york', 'north carolina', 'north dakota', 'ohio', 'oklahoma', 'oregon', 'pennsylvania', 'rhode island', 'south carolina', 'south dakota', 'tennessee', 'texas', 'utah', 'vermont', 'virginia', 'washington', 'west virginia', 'wisconsin', 'wyoming']
us_states_codes = {'AL', 'AK', 'AS', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'DC', 'FL', 'GA', 'GU', 'HI', 'ID', 'IL', 'IN', 'IA', 'KS', 'KY', 'LA', 'ME', 'MD', 'MH', 'MA', 'MI', 'FM', 'MN', 'MS', 'MO', 'MT', 'NE', 'NV', 'NH', 'NJ', 'NM', 'NY', 'NC', 'ND', 'MP', 'OH', 'OK', 'OR', 'PW', 'PA', 'PR', 'RI', 'SC', 'SD', 'TN', 'TX', 'UT', 'VT', 'VA', 'VI', 'WA', 'WV', 'WI', 'WY'}
ca_provinces = ['alberta', 'british columbia', 'manitoba', 'new brunswick', 'newfoundland and labrador', 'nova scotia', 'ontario', 'prince edward island', 'quebec', 'saskatchewan']
ca_provinces_codes = {'AB', 'BC', 'MB', 'NB', 'NL', 'NS', 'NT', 'NU', 'ON', 'PE', 'QC', 'SK', 'YT'}

def get_country_by_code(code=''):
    if code in us_states_codes:
        return "US"
    elif code in ca_provinces_codes:
        return "CA"
    else:
        return "<MISSING>"

def selector(url=''):
    if url:
        r = requests.get(url)
        tree = html.fromstring(r.text.replace('\xa0',' '))
        return {'tree': tree, 'url':url, 'request': r}


class Spider:
    def write_output(self, data):
        if data:
            with open('data.csv', mode='w') as output_file:
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
    return lst[0] if len(lst) > 0 else ''


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
            setattr(self, attr, result or '<MISSING>')
        else:
            raise Exception("No such attribute \"{}\"".format(attr))

    def add_value(self, attr, value, *processors):
        if hasattr(self, attr):
            processors = processors or []
            result = value
            for p in processors:
                result = p(result)
            setattr(self, attr, result or '<MISSING>')
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


