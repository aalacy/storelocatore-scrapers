import csv
import requests
from bs4 import BeautifulSoup
import re
import io
import json
import time

def write_output(data):
    with open('data.csv', mode='w', encoding="utf-8") as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36'
    }
    base_url = "http://www.applebeescanada.com/restaurants/location-finder"
    r = requests.get(base_url, headers=headers)
    soup = BeautifulSoup(r.text, "lxml")
    return_main_object = []
    exists = soup.find('div', {'class', 'location'})
    for data in exists.findAll('a'):
        if data.get('href') == '' or data.get('href') is None:
            city = data.get_text().strip()
        else:
            data_url = "http://www.applebeescanada.com" + data.get('href')
            print(data_url)
            detail_url = requests.get(data_url, headers=headers)
            detail_soup = BeautifulSoup(detail_url.text, "lxml")
            detail_block = detail_soup.find('div', {'class', 'blocks'})
            if detail_block:
                location_name = detail_soup.find('h1').get_text().strip()
                address = detail_block.find('h5').get_text().strip().split(',')
                street_address = ''.join(address[:-1]).strip()
                zip = address[-1].strip()
                phone = detail_block.find('h5').find_next('h3').get_text().strip()[5:]
                if "Meet" in detail_block.find('h5').find_next('p').find_next('p').get_text().strip():
                    hours_of_operation = detail_block.find('h5').find_next('p').get_text().strip()
                else:
                    hours_of_operation = detail_block.find('h5').find_next('p').get_text().strip() + ", " + detail_block.find('h5').find_next('p').find_next('p').get_text().strip()
                store = []
                store.append(data_url)
                store.append(location_name)
                store.append(street_address)
                store.append(city)
                store.append("<MISSING>")
                store.append(zip)
                store.append("CA")
                store.append("<MISSING>")
                store.append(phone)
                store.append("Applebees Grill & Bar")
                store.append("<MISSING>")
                store.append("<MISSING>")
                store.append(hours_of_operation)
                return_main_object.append(store)
            else:
                pass
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)
scrape()