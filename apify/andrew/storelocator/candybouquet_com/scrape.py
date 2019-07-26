import csv
import re

import requests
from bs4 import BeautifulSoup

BASE_URL = 'http://candybouquet.com/where-to-order/default.asp?Zip=&Abbr=&Country={}'

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)

def clean_text(string):
    string = ''.join([i if ord(i) < 128 else ' ' for i in string]) \
        .replace('\r', '') \
        .replace('\t', '') \
        .replace('\n', '')
    return string.strip()

def parse_address(address):
    city, _address = [item.strip() for item in address.split(',')]
    if len(_address.split()) == 2:
        state, zipcode = _address.split()
    else:
        state, zipcode = '<INACCESSIBLE>', '<INACCESSIBLE>'
    return city, state, zipcode

def fetch_phone_hours(store_data):
    phone, hours = '<MISSING>', '<MISSING>'
    for item in store_data:
        if 'Phone' in item:
            phone = re.findall(r'<\/strong>(.*)<br\/>', item)[0].strip()
        if 'Store Hours' in item:
            hours = re.findall(r'<\/strong>(.*)<br\/>', item)[0].strip()
    return phone, hours

def fetch_data():
    data = []
    for idx, country in enumerate(['UNITED+STATES', 'CANADA']):
        url = BASE_URL.format(country)
        res = requests.get(url)
        soup = BeautifulSoup(res.content, 'html.parser')
        stores = soup.select('p.listing')
        for store in stores:
            location_name = store.select_one('strong.store').text
            store_number = location_name.split('#')[-1]
            store = clean_text(store.decode_contents())
            store_data = store.split('<strong>')
            address = [
                item
                for item in store_data[0].split('<br/>')[1:]
                if len(item)
            ]
            del address[-1]
            if len(address) == 1:
                address = ['<MISSING>'] + address
            street_address = address[0]
            try:
                city, state, zipcode = parse_address(address[1])
            except:
                print(address[1])
            country_code = 'US' if idx == 0 else 'CA'
            phone, hours_of_operation = fetch_phone_hours(store_data)
            location_type = 'Candy Bouquet Retail' if 'Retail' in location_name else 'Candy Bouquet Store'
            data.append([
                'http://candybouquet.com/',
                location_name,
                street_address,
                city,
                state,
                zipcode,
                country_code,
                store_number,
                phone,
                location_type,
                '<MISSING>',
                '<MISSING>',
                hours_of_operation
            ])
    return data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()