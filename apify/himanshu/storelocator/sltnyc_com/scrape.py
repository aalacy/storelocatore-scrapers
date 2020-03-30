import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import io
import json


session = SgRequests()

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
    base_url = "https://sltnyc.com/studios/"
    r = session.get(base_url, headers=headers)
    soup = BeautifulSoup(r.text, "lxml")
    return_main_object = []
    address = []
    exists = soup.find('div', {'class', 'studio-grid__inner'})
    if exists:
        for data in soup.findAll('div', {'class', 'studio-grid__inner'}):
            print(data.find('a').get('href'))
            location_name = data.select('.studio-grid__title')[0].get_text()
            address = data.select('.studio-grid__description')[0].get_text().strip().replace('\n', ',').split(',')
            if len(address) == 3:
                street_address = address[0]
                city = address[1]
                state_val = ' '.join(address[-1].strip().split(' ')[:-1])
                if state_val == "New York":
                    state = 'NY'
                else:
                    state = ' '.join(address[-1].strip().split(' ')[:-1])
                zip = address[-1].strip().split(' ')[-1]
            else:
                street_address = address[0] + " " + address[1]
                city = address[2]
                state_val = address[3].strip().split(' ')[0]
                if state_val == "New York":
                    state = 'NY'
                else:
                    state = address[3].strip().split(' ')[0]
                zip = address[3].strip().split(' ')[1]
            detail_url = session.get(data.find('a').get('href'), headers=headers)
            detail_soup = BeautifulSoup(detail_url.text, "lxml")
            if detail_soup.find('a', {'class', 'hero__direction-link'}):
                if "@" in detail_soup.find('a', {'class', 'hero__direction-link'}).get('href'):
                    latitude = detail_soup.find('a', {'class', 'hero__direction-link'}).get('href').split('@')[1].split(',')[0]
                    longitude = detail_soup.find('a', {'class', 'hero__direction-link'}).get('href').split('@')[1].split(',')[1]
                else:
                    latitude = "<MISSING>"
                    longitude = "<MISSING>"
            else:
                latitude = "<MISSING>"
                longitude = "<MISSING>"
            phone = detail_soup.find('div', {'class', 'hero__direction-content'}).findAll('a')[-1].get_text()
            store = []
            store.append(data.find('a').get('href'))
            store.append(location_name)
            store.append(street_address)
            store.append(city)
            store.append(state)
            store.append(zip)
            store.append("US")
            store.append("<MISSING>")
            store.append(phone)
            store.append("SLT")
            store.append(latitude)
            store.append(longitude)
            store.append("<MISSING>")
            return_main_object.append(store)
        return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)
scrape()