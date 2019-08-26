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
    base_url = "http://www.cremedelacrepe.com/"
    r = requests.get(base_url, headers=headers)
    soup = BeautifulSoup(r.text, "lxml")
    return_main_object = []
    exists = soup.find('ul', {'class', 'sub-menu'})
    if exists:
        for data in exists.findAll('a'):
            detail_url = requests.get(data.get('href'), headers=headers)
            detail_soup = BeautifulSoup(detail_url.text, "lxml")
            location_name = detail_soup.find('h1').get_text()
            address = detail_soup.find('div', {'class', 'wpb_wrapper'}).find_next('div', {'class', 'wpb_wrapper'}).find('p').text.replace('\n', ',').strip().split(',')
            street_address = ' '.join(address[:-2])
            city = location_name
            state = address[-2].strip().split(' ')[0]
            zip = address[-2].strip().split(' ')[1]
            phone = address[-1][7:]
            store = []
            store.append(data.get('href'))
            store.append(location_name)
            store.append(street_address)
            store.append(city)
            store.append(state)
            store.append(zip)
            store.append("US")
            store.append("<MISSING>")
            store.append(phone)
            store.append("Creme de la Crepe")
            store.append("<MISSING>")
            store.append("<MISSING>")
            store.append("<MISSING>")
            return_main_object.append(store)
        return return_main_object
def scrape():
    data = fetch_data()
    write_output(data)
scrape()
