import csv
import requests
from bs4 import BeautifulSoup
import re
import json


def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    header = {'User-agent': 'Mozilla/5.0 (Windows; U; Windows NT 5.1; de; rv:1.9.1.5) Gecko/20091102 Firefox/3.5.5'}
    return_main_object = []
    base_url = "https://www.theoopsco.com/"
    r = requests.get("https://www.theoopsco.com/our-locations", headers=header)
    soup = BeautifulSoup(r.text, "lxml")
    for x in soup.find_all('div',{'class':'c4inlineContent'}):
        locator_domain  = base_url
        location_name = x.text.strip().split('\n')[0].strip()
        street_address = x.text.strip().split('\n')[1].strip()
        city = ''
        state = ''
        zip = ''
        country_code = 'US'
        store_number = ''
        phone = x.text.strip().split('\n')[2].strip()
        location_type = '<MISSING>'
        latitude = ''
        longitude = ''
        hours_of_operation =  x.text.strip().split('\n')[5].strip() + ' ' +x.text.strip().split('\n')[6].strip() + ' ' +x.text.strip().split('\n')[7].strip()
        page_url = "https://www.theoopsco.com/our-locations"



        store = []
        store.append(locator_domain if locator_domain else '<MISSING>')
        store.append(location_name if location_name else '<MISSING>')
        store.append(street_address if street_address else '<MISSING>')
        store.append(city if city else '<MISSING>')
        store.append(state if state else '<MISSING>')
        store.append(zip if zip else '<MISSING>')
        store.append(country_code if country_code else '<MISSING>')
        store.append(store_number if store_number else '<MISSING>')
        store.append(phone if phone else '<MISSING>')
        store.append(location_type if location_type else '<MISSING>')
        store.append(latitude if latitude else '<MISSING>')
        store.append(longitude if longitude else '<MISSING>')

        store.append(hours_of_operation if hours_of_operation else '<MISSING>')
        store.append(page_url if page_url else '<MISSING>')
        return_main_object.append(store)
    return return_main_object


def scrape():
    data = fetch_data()

    write_output(data)


scrape()
