import csv
import requests
from bs4 import BeautifulSoup
import re
import json

def write_output(data):
    with open('data.csv', mode='w', encoding="utf-8") as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36'
    }
    base_url = "https://pizzapiecafe.co/locations/"
    r = requests.get(base_url, headers=headers)
    soup = BeautifulSoup(r.text, "lxml")
    return_main_object = []
    address = []
    for data in soup.findAll('div', {'class', 'location-drawer'}):
        location_name = data.find('h1').get_text().strip()
        full_add = data.select('tr')[5].find('td').get_text().strip()
        street_state_city = full_add.split(' ')
        city = street_state_city[len(street_state_city) - 2]
        state = street_state_city[len(street_state_city) - 1]
        street_address = ' '.join(street_state_city[:-2])
        phone = data.select('tr')[7].find('td').get_text().strip()
        hours_of_operation = data.select('tr')[9].find('td').get_text() + " " + (data.select('tr')[9].find('td').find_next('td').get_text() + ", " + data.select('tr')[10].find('td').get_text() + " " + (data.select('tr')[10].find('td').find_next('td').get_text()))

        store = []
        store.append(base_url)
        store.append(location_name)
        store.append(street_address)
        store.append(city)
        store.append(state)
        store.append("<MISSING>")
        store.append("US")
        store.append("<MISSING>")
        store.append(phone)
        store.append("<MISSING>")
        store.append("<MISSING>")
        store.append("<MISSING>")
        store.append(hours_of_operation)
        return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
