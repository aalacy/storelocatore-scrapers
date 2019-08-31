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
    base_url = "http://eatdefelice.com/locations/"
    r = requests.get(base_url, headers=headers)
    soup = BeautifulSoup(r.text, "lxml")
    return_main_object = []
    for data in soup.findAll('td', {'class', 'bodytxt'}):
        i = 0
        state_val = ''
        for val in data.get_text().replace('\n', ',').split(','):
            if i == 0:
                state_val = val
            else:
                if len(val.split(' ')) == 3:
                    city = val.split(' ')[0] + " " + val.split(' ')[1]
                    phone = val.split(' ')[2]
                elif len(val.split(' ')) == 2:
                    city = val.split(' ')[0]
                    phone = val.split(' ')[1]
                store = []
                store.append(base_url)
                store.append("<MISSING>")
                store.append("<MISSING>")
                store.append(city)
                store.append(state_val)
                store.append("<MISSING>")
                store.append("US")
                store.append("<MISSING>")
                store.append(phone)
                store.append("DeFelice Bros. Pizza")
                store.append("<MISSING>")
                store.append("<MISSING>")
                store.append(soup.select('span.bodytxt')[0].get_text().replace('\n', ''))
                return_main_object.append(store)
            i = i + 1
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)
scrape()
