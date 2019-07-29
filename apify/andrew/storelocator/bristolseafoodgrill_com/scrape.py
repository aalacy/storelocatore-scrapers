import csv
import requests
from bs4 import BeautifulSoup
import json

BASE_URL = 'https://bristolseafoodgrill.com'

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)

def parse_address(address):
    try:
        city, _address = address.split(',')
        state, zip_code = _address.strip().split()
    except:
        city, state, zip_code = [item.strip() for item in address.split(',')]
    return city, state, zip_code

def remove_non_ascii_characters(string):
    return ''.join([i if ord(i) < 128 else ' ' for i in string])

def fetch_geo(data):
    return data['geo']['latitude'], data['geo']['longitude']

def convert_geo(geo):
    geo = [
        item.replace('\'', '').replace('"', '')
        for item in remove_non_ascii_characters(geo).split()
    ]
    geo = "-".join(geo[:-1])+geo[-1]
    multiplier = 1 if geo[-1] in ['N', 'E'] else -1
    return multiplier * sum(float(x) / 60 ** n for n, x in enumerate(geo[:-1].split('-')))

def fetch_data():
    data = []
    res = requests.get(BASE_URL)
    soup = BeautifulSoup(res.content, 'html.parser')
    restaurant_urls = [
        BASE_URL + a_tag['href']
        for a_tag in soup.select('div.landingContact > a.lightLink')
    ]
    for url in restaurant_urls:
        res = requests.get(url)
        soup = BeautifulSoup(res.content, 'html.parser')
        location_name = soup.select_one('h2.formTitleDark').text
        street_address = soup.select_one('div.restaurantAddress > p.bc1RegularLargeDark:nth-of-type(1)').text
        _address = soup.select_one('div.restaurantAddress > p.bc1RegularLargeDark:nth-of-type(2)').text
        city, state, zipcode = parse_address(_address)
        phone = soup.select_one('div.restaurantAddress > p.bc1RegularLargeDark:nth-of-type(3)').text
        country_code = 'US'
        hours_of_operation = remove_non_ascii_characters(soup.select_one('div.bc1RegularLargeDark.hours').text)
        try:
            lat, lon = fetch_geo(json.loads(soup.select_one("script[type*='application']").text))
        except:
            geo = [
                p.text
                for p in soup.select('div.locationCoordinates p')
            ][2:]
            lat, lon = [convert_geo(item) for item in geo]
        data.append([
            BASE_URL,
            location_name,
            street_address,
            city,
            state,
            zipcode,
            'US',
            '<MISSING>',
            phone,
            '<MISSING>',
            lat,
            lon,
            hours_of_operation
        ])
    return data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()