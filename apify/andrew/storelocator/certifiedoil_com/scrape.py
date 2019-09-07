import csv
import re

import requests
from bs4 import BeautifulSoup

BASE_URL = 'https://www.certifiedoil.com/'

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)

def remove_non_ascii_characters(string):
    return ''.join([i if ord(i) < 128 else ' ' for i in string]).strip()

def parse_address(address):
    street_address = address[0]
    phone = address[2]
    city, _address = address[1].split(',')
    state, zipcode = _address.split()
    return street_address, city, state, zipcode, phone

def parse_geo(url):
    lon = re.findall(r'2d{1}(-?\d*.{1}\d*)!{1}', url)[0]
    lat = re.findall(r'3d{1}(-?\d*.{1}\d*)!{1}', url)[0]
    return lat, lon

def fetch_data():
    data = []
    res = requests.get('https://www.certifiedoil.com/Locations.aspx')
    soup = BeautifulSoup(res.content, 'html.parser')
    state_urls = [
        BASE_URL + a['href']
        for a in soup.select('ul#menu > li:nth-child(3) li > a')
    ]
    for state_url in state_urls:
        res = requests.get(state_url)
        soup = BeautifulSoup(res.content, 'html.parser')
        store_urls = [
            BASE_URL + a['href']
            for a in soup.select('ul#menu > li > ul > li > a')
        ]
        for store_url in store_urls:
            res = requests.get(store_url)
            soup = BeautifulSoup(res.content, 'html.parser')
            location_name = soup.select_one('h1').text
            store_number = location_name.split('#')[-1].strip()
            for col in soup.select('table td'):
                header = col.select_one('strong') or col.select_one('span')
                if 'Hours' in header.text:
                    hours_of_operation = " ".join([
                        li.text
                        for li in col.select('li')
                    ])
                    hours_of_operation = remove_non_ascii_characters(hours_of_operation)
            address = [
                el.text.strip()
                for el in soup.select('span.textwindow_text')[-1].select('div')
                if len(el.text.strip())
            ]
            if len(address) == 1:
                address = soup.select('span.textwindow_text')[-1].decode_contents()
                address = address.split('</div>')[1:]
                street_address, _address = address[0].split('<br/>')
                phone = address[1]
                address = [street_address, _address, phone]
            if len(address) == 2:
                address = soup.select('span.textwindow_text')[-1].decode_contents()
                address = address.split('</div>')[1:]
                address[:2] = address[0].split('<br/>')
            address = [
                remove_non_ascii_characters(item.replace('<div>', ''))
                for item in address
                if len(item)
            ]
            street_address, city, state, zipcode, phone = parse_address(address)
            try:
                lat, lon = parse_geo(soup.select_one('span > iframe')['src'])
            except TypeError:
                lat, lon = '<MISSING>', '<MISSING>'
            # Incorrect iFrames on website for these store numbers
            if store_number in ['281', '202']:
                lat, lon = '<INACCESSIBLE>', '<INACCESSIBLE>'
            data.append([
                BASE_URL,
                location_name,
                street_address,
                city,
                state,
                zipcode,
                'US',
                store_number,
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