import csv
import requests
from bs4 import BeautifulSoup
import re
import io
import json

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
    base_url = "https://www.chilis.com/locations/us/all"
    r = requests.get(base_url, headers=headers)
    soup = BeautifulSoup(r.text, "lxml")
    return_main_object = []
    for values in soup.findAll('a', {'class', 'city-link'}):
        detail_page_url = "https://www.chilis.com" + values.get('href')
        print(detail_page_url)
        detail_url = requests.get(detail_page_url, headers=headers)
        detail_soup = BeautifulSoup(detail_url.text, "lxml")
        detail_page_exits = detail_soup.find('div', {'class', 'location-results'})
        if detail_page_exits:
            for data in detail_page_exits.findAll('div', {'class', 'location'}):
                location_name = data.select('.location-title')[0].get_text()
                if data.find('div', {'class', 'location-body'}):
                    address = data.find('div', {'class', 'location-body'})
                    city = values.get_text()
                    detail_address = address.find('div').get_text().strip().split(',')
                    if len(detail_address) == 3:
                        street_address = detail_address[0].strip() + "," + detail_address[1].strip()
                        state = detail_address[2].strip().split(' ')[0]
                        zip = detail_address[2].strip().split(' ')[1]
                    if len(detail_address) == 2:
                        street_address = detail_address[0].strip()
                        state = detail_address[1].strip().split(' ')[0]
                        zip = detail_address[1].strip().split(' ')[1]
                    else:
                        state = "<MISSING>"
                        zip = "<MISSING>"
                    if data.find('a', {'class', 'location-phone'}):
                        phone = data.find('a', {'class', 'location-phone'}).get_text()
                    else:
                        phone = "<MISSING>"
                    store = []
                    store.append(detail_page_url)
                    store.append(location_name)
                    store.append(street_address)
                    store.append(city)
                    store.append(state)
                    store.append(zip)
                    store.append("US")
                    store.append("<MISSING>")
                    store.append(phone)
                    store.append("Chili's Grill & Bar - Local Restaurants Near Me | Chili's")
                    store.append("<MISSING>")
                    store.append("<MISSING>")
                    store.append("<MISSING>")
                    return_main_object.append(store)
                else:
                    pass
        else:
            pass
    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)
scrape()