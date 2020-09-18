import csv
from collections import defaultdict

class Scrape:
    def __init__(self, url):
        self.url = url
        self.CHROME_DRIVER_PATH = 'chromedriver'

    def write_output(self, data):
        with open('data.csv', mode='w') as output_file:
            writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

            # Header
            writer.writerow([
                "locator_domain",
				"page_url",
                "location_name",
                "street_address",
                "city",
                "state",
                "zip",
                "country_code",
                "store_number",
                "phone",
                "location_type",
                "latitude",
                "longitude",
                "hours_of_operation"
            ])
            # Body
            for row in data:
                writer.writerow(row)

    def etree_to_dict(self, t):
        d = {t.tag: {} if t.attrib else None}
        children = list(t)
        if children:
            dd = defaultdict(list)
            for dc in map(self.etree_to_dict, children):
                for k, v in dc.items():
                    dd[k].append(v)
            d = {t.tag: {k: v[0] if len(v) == 1 else v
                         for k, v in dd.items()}}
        if t.attrib:
            d[t.tag].update(('@' + k, v)
                            for k, v in t.attrib.items())
        if t.text:
            text = t.text.strip()
            if children or t.attrib:
                if text:
                    d[t.tag]['#text'] = text
            else:
                d[t.tag] = text

        return d

    def fetch_data(self):
        pass

    def scrape(self):
        self.fetch_data()
        self.write_output(self.data)
