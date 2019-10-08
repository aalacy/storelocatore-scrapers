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
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36'
    }
    base_url = "https://www.ihg.com/kimptonhotels/content/us/en/stay/find-a-hotel#location=all"
    r = requests.get(base_url, headers=headers)
    soup = BeautifulSoup(r.text, "lxml")
    return_main_object = []
    for data in soup.findAll('div', {'class', 'hotel-tile-info-wrapper'}):
        data_url = "https:" + data.find('a').get('href')
        print(data_url)
        detail_url = requests.get(data_url, headers=headers)
        detail_soup = BeautifulSoup(detail_url.text, "lxml")
        detail_block = detail_soup.select('.brand-logo .visible-content')
        if detail_block:
            location_name = detail_soup.select('.name')[0].get_text().strip()
            phone = detail_soup.select('.phone-number')[0].get_text().strip()[8:]
            for br in detail_soup.select('.brand-logo .visible-content')[0].find_all("br"):
                br.replace_with(",")
            address = detail_soup.select('.brand-logo .visible-content')[0].get_text().strip().split(',')
            street_address = ' '.join(address[:-2]).strip()
            if len(address[-2].split(" ")) == 2:
                city = address[-2].split(" ")[0].strip()
                state = address[-2].split(" ")[0].strip()
                zip = address[-2].split(" ")[1].strip()
            else:
                city = ' '.join(address[-2].split(' ')[:-2])
                state = address[-2].strip().split(' ')[-2]
                zip = address[-2].strip().split(' ')[-1]
            store = []
            store.append(data_url)
            store.append(location_name)
            store.append(street_address)
            store.append(city)
            store.append(state)
            store.append(zip)
            store.append("US")
            store.append("<MISSING>")
            store.append(phone)
            store.append("Kimpton Hotels")
            store.append("<MISSING>")
            store.append("<MISSING>")
            store.append("<MISSING>")
            return_main_object.append(store)
        else:
            pass
    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
