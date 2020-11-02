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
    base_url = "https://piezonis.com/locations/"
    r = session.get(base_url, headers=headers,verify=False)
    soup = BeautifulSoup(r.text, "lxml")
    return_main_object = []
    address = []
    soup.findAll('div', {'class', 'location-container'})[-1]
    for state in soup.findAll('div', {'class', 'location-container'}):
        if state.find('a'):
            state_request = session.get(state.find('a').get('href'), headers=headers,verify=False)
            state_soup = BeautifulSoup(state_request.text,'lxml')
            store = []
            name_statcode = state_soup.select('div#location-box')[0].find('h1').get_text().strip().split(',')
            store_name = name_statcode[0]
            country_code = name_statcode[1]
            store.append(base_url)
            store.append(state_soup.find('h1').text)
            store.append(state_soup.select('div#location-box')[0].find('h2').get_text())
            store.append(store_name)
            store.append(country_code)
            store.append(state.findAll('p')[-2].get_text().strip()[-5:])
            store.append("US")
            store.append("<MISSING>")
            store.append(state_soup.select('div#location-box')[0].find('p', {'class', 'phone'}).get_text().strip())
            store.append("pie zonis")
            store.append("<INACCESSIBLE>")
            store.append("<INACCESSIBLE>")
            store.append(state_soup.select('div#location-box')[0].find('p', {'class', 'phone'}).find_next('div').get_text() + " " + state_soup.select('div#location-box')[0].find('p', {'class', 'phone'}).find_next('div').find_next('p').get_text().replace("\n"," "))
            return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)
scrape()
