import csv
import re
import json
import requests
from bs4 import BeautifulSoup

BASE_URL = 'https://www.steinmart.com'
MISSING = '<MISSING>'
INACCESSIBLE = '<INACCESSIBLE>'

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_street_address(address):
    return " ".join([
        address[key]
        for key in ['street1', 'street2', 'street3']
        if address[key]
    ])


def fetch_data():
    data = []
    res = requests.get('https://www.steinmart.com/store-locator/all-stores.do')
    soup = BeautifulSoup(res.content, 'html.parser')
    store_urls = [
        BASE_URL + a_tag['href']
        for a_tag in soup.select('div.ml-storelocator-item-wrapper a')
    ]
    for idx, store_url in enumerate(store_urls):
        res = requests.get(store_url)
        soup = BeautifulSoup(res.content, 'html.parser')
        script = [
            script.text
            for script in soup.select('script[type="text/javascript"]')[-11:]
            if 'latitude' in script.text
        ][0]
        script = json.loads(re.findall(r'{.*}', script)[0])
        store_data = script['results'][0]
        address = store_data['address']
        street_address = fetch_street_address(address)
        hours_of_operation = " | ".join([
            tr.text.strip()
            for tr in soup.select('div.ml-storelocator-hours tr')
        ])
        zipcode = address.get('postalCode')
        if len(zipcode) == 4:
            zipcode = '0' + zipcode
        phone = address.get('phone')
        if not sum(c.isdigit() for c in phone) == 10:
            phone = INACCESSIBLE
        data.append([
            BASE_URL,
            store_data.get('name'),
            street_address,
            address.get('city'),
            address.get('stateCode'),
            zipcode,
            address.get('countryName'),
            store_data.get('id'),
            phone,
            MISSING,
            store_data.get('location', {}).get('latitude'),
            store_data.get('location', {}).get('longitude'),
            hours_of_operation
        ])
    return data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
