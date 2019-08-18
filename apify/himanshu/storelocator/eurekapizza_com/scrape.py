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
    base_url = "https://www.eurekapizza.com/locations/"
    r = requests.get(base_url, headers=headers)
    soup = BeautifulSoup(r.text, "lxml")
    return_main_object = []
    data = soup.select('.vc_row.wpb_row.vc_row-fluid')
    for values in data:
        details = values.select('.vc_col-sm-6')
        for val in details:
            location_name = val.find('h2').get_text()
            street_address = val.find('h5').find_next('p').get_text()
            city_state_pin = val.find('h5').find_next('p').find_next('p').get_text()
            city_state_pin_values = city_state_pin.split(' ')
            city = ' '.join(city_state_pin_values[:-2])[:-1]
            state = city_state_pin_values[-2]
            zip = city_state_pin_values[-1]
            store_val = val.select('.vc_btn3-container.vc_btn3-center')[0].find('a').get('href')
            if store_val[-4:].isdigit():
                store_number = store_val[-4:]
            else:
                store_number = store_val[-7:-3]
            phone_value = val.select('.vc_btn3-container.vc_btn3-center')[0].find_next('div').find('p')
            if 'Phone:' in phone_value:
                phone = phone_value.split('[')[0]
            else:
                phone_data = val.select('.vc_btn3-container.vc_btn3-center')[0].find_next('div').text
                phone = phone_data.split('[')[0]
            latLongDetails = val.find('h5').find_next('p').find_next('p').find_next('p').find('a').get('href')
            if '@' in latLongDetails:
                latLong = latLongDetails.split('@')
                latitude = latLong[1].split(',')[0]
                longitude = latLong[1].split(',')[1]
            else:
                latitude = "<INACCESSIBLE>"
                longitude ="<INACCESSIBLE>"
            hours_of_operation = val.find('h5').find_next('h5').find_next('p').get_text() + ", " + val.find('h5').find_next('h5').find_next('p').find_next('p').get_text()
            store = []
            store.append(base_url)
            store.append(location_name)
            store.append(street_address)
            store.append(city)
            store.append(state)
            store.append(zip)
            store.append("US")
            store.append(store_number)
            store.append(phone)
            store.append("Eureka Pizza")
            store.append(latitude)
            store.append(longitude)
            store.append(hours_of_operation)
            return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)
scrape()
