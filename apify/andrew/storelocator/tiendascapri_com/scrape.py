import csv
import re

import requests
from bs4 import BeautifulSoup

BASE_URL = 'http://tiendascapri.com/tiendas'

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)

def parse_address(address):
    address = [item.strip() for item in address.split(',')]
    if len(address) == 3:
        address = ['<MISSING>'] + address
    if len(address) == 5:
        address[:2] = [" ".join(address[:2])]
    address[2] = str(address[2])
    if not address[2].isdigit():
        address[:2] = [" ".join(address[:2])]
        street_address = address[0].replace('<MISSING>', '')
        state = address[2]
        zipcode = "".join([s for s in address[1].split() if s.isdigit()])
        city = address[1].replace(zipcode, '').strip()
        return street_address, city, zipcode, state
    return address[0], address[1], address[2], address[3]

def fetch_data():
    data = []
    res = requests.get(BASE_URL)
    soup = BeautifulSoup(res.content, 'html.parser')
    stores = [
        [h4] + h4.find_next_siblings('p')
        for h4 in soup.select('div.column_attr > h4')
    ]
    for store in stores:
        location_name = store[0].text
        address = store[1].text
        phone = store[2].text
        if not re.match(r'\d{3}[-]{1}\d{3}[-]{1}\d{4}', phone):
            phone = '<MISSING>'
        street_address, city, zipcode, state = parse_address(address)
        data.append([
            'http://tiendascapri.com',
            location_name,
            street_address,
            city,
            state,
            zipcode,
            'US',
            '<MISSING>',
            phone,
            '<MISSING>',
            '<MISSING>',
            '<MISSING>',
            '<MISSING>'
        ])
    return data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()