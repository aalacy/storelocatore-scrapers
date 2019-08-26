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
    base_url = "https://www.graduatehotels.com"
    r = requests.get(base_url, headers=headers)
    soup = BeautifulSoup(r.text, "lxml")
    return_main_object = []
    address = []
    exists = soup.find('a', {'class', 'js-location-toggle'})
    if exists:
        for data in soup.findAll('a', {'class', 'hotel-location'}):
            if data.get('href') == "#":
                pass
            else:
                print(data.get('href'))
                detail_url = requests.get(data.get('href'), headers=headers)
                detail_soup = BeautifulSoup(detail_url.text, "lxml")
                if detail_soup.find('div', {'class', 'footer-address'}):
                    for br in detail_soup.find('div', {'class', 'footer-address'}).select('.lead')[0].findAll('br'):
                        br.replace_with("\n")
                    location_name = data.get_text()
                    address = detail_soup.find('div', {'class', 'footer-address'}).select('.lead')[0].get_text().split('\n')
                    if len(address) == 4:
                        street_address = address[0].strip()
                        city = data.select('.location-name')[0].get_text().strip()
                        state = data.select('.location-state')[0].get_text().strip()
                        zip_val = address[-1].strip()
                        if len(str(zip_val)) > 6:
                            zip = address[1].split(',')[1].split(' ')[-1]
                        else:
                            zip = address[-1].strip()
                    else:
                        street_address = address[0].strip()
                        city = data.select('.location-name')[0].get_text().strip()
                        state = data.select('.location-state')[0].get_text().strip()
                        zip = address[1].split(',')[-1].strip().split(' ')[-1].strip()
                    phone_val = detail_soup.find('div', {'class', 'footer-contact'}).find('a').get('href')[6:].strip()
                    if phone_val[-1].isdigit():
                        phone = detail_soup.find('div', {'class', 'footer-contact'}).find('a').get('href')[6:].strip()
                    else:
                        phone = "<MISSING>"
                    if len(detail_soup.find('a', {'class', 'logo'}).find('img').get('alt').strip()) == 0:
                        location_type = "<MISSING>"
                    else:
                        location_type = detail_soup.find('a', {'class', 'logo'}).find('img').get('alt').strip()
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
                    store.append(location_type)
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
