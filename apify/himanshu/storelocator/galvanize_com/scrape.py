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
    base_url = "https://www.galvanize.com/"
    r = requests.get(base_url, headers=headers)
    soup = BeautifulSoup(r.text, "lxml")
    return_main_object = []
    exists = soup.find('div', {'class', 'nav-items'})
    if exists:
        all_loc = exists.findAll('div')[-2]
        for data in all_loc.findAll('a'):
            print("https://www.galvanize.com" + data.get("href"))
            detail_url = requests.get("https://www.galvanize.com" + data.get("href"), headers=headers)
            detail_soup = BeautifulSoup(detail_url.text, "lxml")
            location_name = detail_soup.find('h3').get_text().strip()
            detail_exists = detail_soup.find('div', {'class', 'description-section'})
            if detail_exists.findAll('p', {'class', 'callout'}):
                address = detail_soup.findAll('p', {'class', 'callout'})[2].text.replace('\n', '').replace('        ', ' ').strip().split(' ')
                city = data.text
                street_address = ' '.join(address[:-2])
                state = address[-2]
                zip = address[-1]
                phone = detail_soup.findAll('p', {'class', 'callout'})[1].get_text().strip()
            else:
                city = "<MISSING>"
                street_address = "<MISSING>"
                state = "<MISSING>"
                zip = "<MISSING>"
                phone = "<MISSING>"
            store = []
            store.append("https://www.galvanize.com" + data.get("href"))
            store.append(location_name)
            store.append(street_address)
            store.append(city)
            store.append(state)
            store.append(zip)
            store.append("US")
            store.append("<MISSING>")
            store.append(phone)
            store.append("Galvanize")
            store.append("<MISSING>")
            store.append("<MISSING>")
            store.append("<MISSING>")
            return_main_object.append(store)
        return return_main_object
    else:
        pass

def scrape():
    data = fetch_data()
    write_output(data)
scrape()
