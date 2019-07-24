import csv
import requests
from bs4 import BeautifulSoup
import re

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    locator_domain = 'https://www.pharmaca.com/'

    ext = 'store-locator'
    to_scrape = locator_domain + ext
    

    page = requests.get(to_scrape)
    assert page.status_code == 200

    soup = BeautifulSoup(page.content, 'html.parser')

    div = soup.find('div', {'id': 'amlocator_left'})
    stores = div.find_all('span', {'name': 'leftLocation'})
    all_store_data = []
    for store in stores:
        location_name = store.find('div', {'class': 'location_header'}).text.strip()
        street_address = store.find('div', {'class': 'location_header'}).nextSibling

        state = street_address.nextSibling.nextSibling

        city_zip = state.nextSibling.nextSibling

        phone_number = city_zip.nextSibling.nextSibling
        street_address = street_address.strip()
        state = state.strip()
        city_zip = city_zip.strip()
        phone_number = phone_number.strip()

        city_zip_arr = city_zip.replace(' ', '').split(',')
        city = city_zip_arr[0]
        zip_code = city_zip_arr[1]
        if not zip_code.isdigit():
            zip_code = '<MISSING>'

        hours = store.find('div', {'class': 'all_schedule'}).text.replace(' ', '').replace('\n', ' ').strip()

        country_code = 'US'
        store_number = '<MISSING>'
        location_type = '<MISSING>'
        lat = '<MISSING>'
        longit = '<MISSING>'
        
        store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code,
                     store_number, phone_number, location_type, lat, longit, hours ]
        all_store_data.append(store_data)
        

    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
