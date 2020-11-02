import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import io
import json
import time


session = SgRequests()

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
    headers1 = {
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36',
        'referrer': 'https://google.com',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'en-US,en;q=0.9',
        'Pragma': 'no-cache',
    }
    base_url = "https://benitospizza.com/choose-your-state/"
    r = session.get(base_url, headers=headers)
    soup = BeautifulSoup(r.text, "lxml")
    return_main_object = []
    address = []
    exists = soup.select("#myDropdown")
    if exists:
        for data in exists[0].findAll('a'):
            detail_url = session.get(data.get('href'), headers=headers1, timeout=5)
            detail_soup = BeautifulSoup(detail_url.text, "lxml")
            if detail_soup.findAll('table', {'class', 'aligncenter'}):
                for all_values in detail_soup.findAll('table', {'class', 'aligncenter'}):
                    location_name = all_values.find('td').find('h1').get_text()
                    phone = all_values.find('td').find('p').get_text()
                    city_state_pin = all_values.find('td').find('p').find_next('p').find_next('p').get_text().replace('\n', ' ').strip()
                    city_state_pin_val = city_state_pin.split(' ')
                    street_address_post = ' '.join(city_state_pin_val[:-4])[:-1].strip()
                    street_address = all_values.find('td').find('p').find_next('p').get_text() + " " + street_address_post
                    city = city_state_pin_val[-4][:-1]
                    state = city_state_pin_val[-3]
                    zip = city_state_pin_val[-2].strip()
                    hours_of_operation = all_values.find('td').find_next('td').get_text().replace('\n', ' ').strip()[5:]
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
                    store.append("Benito's Pizza | Specialty Pizza Delivery, Specials & Coupons, Wings, Pasta")
                    store.append("<INACCESSIBLE>")
                    store.append("<INACCESSIBLE>")
                    store.append(hours_of_operation)
                    return_main_object.append(store)
            else:
                exists_data = detail_soup.find('div', {'class', 'module-text'})
                if exists_data.find('h1').get_text().isspace():
                    location_name = exists_data.find('h1').find_next('h1').get_text()
                    street_address = exists_data.find('h1').find_next('h1').find_next('h1').get_text()
                    hours_of_operation = exists_data.find('h3').find_next('p').text + ", " + exists_data.find('h3').find_next('p').find_next('p').text + ", " + exists_data.find('h3').find_next('p').find_next('p').find_next('p').text
                    phone = exists_data.find('h3').find_next('p').find_next('p').find_next('p').find_next('p').find_next('p').findAll('span')[-4].find('a').get('href')[6:]
                    city = "<MISSING>"
                    state = "<MISSING>"
                    zip = "<MISSING>"
                else:
                    location_name = exists_data.find('h1').get_text()
                    address = exists_data.find('h1').find_next('h1').get_text().split(' ')
                    street_address = ' '.join(address[:-3])[:-1]
                    city = address[-3]
                    state = address[-2]
                    zip = address[-1]
                    hours_of_operation = exists_data.find('h3').find_next('p').text + ", " + exists_data.find('h3').find_next('p').find_next('p').text + ", " + exists_data.find('h3').find_next('p').find_next('p').find_next('p').text + ", " + exists_data.find('h3').find_next('p').find_next('p').find_next('p').find_next('p').text
                    phone = exists_data.find('h3').find_next('p').find_next('p').find_next('p').find_next('p').find_next('p').findAll('span')[-4].find('a').get('href')[6:]
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
                store.append("Benito's Pizza | Specialty Pizza Delivery, Specials & Coupons, Wings, Pasta")
                store.append("<INACCESSIBLE>")
                store.append("<INACCESSIBLE>")
                store.append(hours_of_operation)
                return_main_object.append(store)
        return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
