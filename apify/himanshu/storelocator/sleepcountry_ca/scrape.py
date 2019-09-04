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
    base_url = "https://www.sleepcountry.ca/find-a-store"
    r = requests.get(base_url, headers=headers)
    soup = BeautifulSoup(r.text, "lxml")
    return_main_object = []
    exists = soup.find('ol', {'class', 'store-list'})
    if exists:
        for data in exists.findAll('li'):
            location_name = data.find('h3').get_text().split('\n')[-1]
            address = data.find('address').get_text().strip().replace('\n', ',').split(',')
            if "Charlottetown" in location_name:
                street_address = address[0]
                zip_state = address[1].split(' ')
                city = ' '.join(zip_state[2:])
                zip = ' '.join(zip_state[:2])
            else:
                if len(address) == 4:
                    street_address = address[0].strip() + " " + address[1].strip()
                    zip_state = address[2].split(' ')
                    city = ' '.join(zip_state[2:])
                    zip = ' '.join(zip_state[:2])
                else:
                    street_address = address[0]
                    zip_state = address[1].split(' ')
                    city = ' '.join(zip_state[2:])
                    zip = ' '.join(zip_state[:2])
                phone = data.find('address').find_next('p').get_text().replace('Phone: ', '')
                latAndLong = data.find('address').find_next('a').get('href')
                if "@" in latAndLong:
                    latitude = latAndLong.split('@')[1].split(',')[0]
                    longitude = latAndLong.split('@')[1].split(',')[1]
                else:
                    latitude = "<MISSING>"
                    longitude = "<MISSING>"
            store = []
            store.append(base_url)
            store.append(location_name)
            store.append(street_address)
            store.append(city)
            store.append("<MISSING>")
            store.append(zip)
            store.append("CA")
            store.append("<MISSING>")
            store.append(phone)
            store.append("Sleep Country Canada")
            store.append(latitude)
            store.append(longitude)
            store.append("<MISSING>")
            return_main_object.append(store)
    else:
        pass
    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)
scrape()