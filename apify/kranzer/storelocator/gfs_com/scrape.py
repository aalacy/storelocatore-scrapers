import csv
import re
import requests
import json
from w3lib.html import remove_tags

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    data = []
    locator_domain = "https://gfsstore.com/locations/"
    base_url = "https://gfsstore.com/"
    r = requests.get(base_url+'stores_jsonp/?callback=jQuery112408348595095024478_1564832094867')
    locations = json.loads(re.findall(r'.+?\((.+)\)', r.text)[0])
    for location in locations:
        l_ = []
        l_.append(locator_domain)
        l_.append(location['title'] or "<MISSING>")
        l_.append(location['field_address'][0]['thoroughfare'] or "<MISSING>")
        l_.append(location['field_address'][0]['locality'] or "<MISSING>")
        l_.append(location['field_address'][0]['administrative_area'] or "<MISSING>")
        l_.append(location['field_address'][0]['postal_code'] or "<MISSING>")
        l_.append(location['field_address'][0]['country'] or "<MISSING>")
        l_.append(location['nid'] or "<MISSING>")
        l_.append(location['field_phone'][0]['safe_value'] or "<MISSING>")
        l_.append(location['field_location_type'][0]['value'] or "<MISSING>")
        l_.append(location['field_latitude'][0]['value'] or "<MISSING>")
        l_.append(location['field_longitude'][0]['value'] or "<MISSING>")
        l_.append(remove_tags(location['field_hours'][0]['safe_value'].replace('<br>', '; ')).strip() or "<MISSING>")
        data.append(l_)
    return data


def scrape():
    data = fetch_data()
    write_output(data)

scrape()