import csv
import requests
from bs4 import BeautifulSoup
import re
import json

def write_output(data):
    with open('lotsa.csv', mode='w', encoding="utf-8") as output_file:
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
    base_url = "https://lotsa.com/locations/"
    r = requests.get(base_url, headers=headers)
    soup = BeautifulSoup(r.text, "lxml")
    return_main_object = []
    address = []
    for data in soup.select('.et_pb_section_5.et_pb_section .et_pb_column.et_pb_column_1_3.et_pb_css_mix_blend_mode_passthrough'):
        state_request = requests.get("https://lotsa.com" + data.find('a').get('href'), headers=headers)
        state_soup = BeautifulSoup(state_request.text,'lxml')
        if data.find('h3'):
            store_name = data.find('h3').get_text().strip()
            phone = data.find('h3').find_next('h3').get_text().strip()
            street_add = data.find('h3').find_next('h3').find_next('p').next_element
            city_state_pin = data.find('h3').find_next('h3').find_next('p').find('br').next_element
            city_state_pin_arr = city_state_pin.split(',')
            city = city_state_pin_arr[0]
            country = city_state_pin_arr[1][1:3]
            pincode = city_state_pin_arr[1][-5:]
        else:
            store_name = data.find('p').find_next('span').get_text()
            phone = data.find('p').find_next('span').find_next('span').get_text()
            street_add = data.find('p').find_next('span').find_next('span').find_next('br').next_element.strip()
            city_state_pin = data.find('p').find_next('span').find_next('span').find_next('br').find_next('br').next_element.strip()
            city_state_pin_arr = city_state_pin.split(',')
            city = city_state_pin_arr[0]
            country = city_state_pin_arr[1][1:3]
            pincode = city_state_pin_arr[1][-5:]
        print("https://lotsa.com" + data.find('a').get('href'))
        if state_soup.select('.et_pb_column_5'):
            hours = state_soup.select('.et_pb_column_5')[0].find('h3').find_next('p').get_text()
        else:
            hours = state_soup.select('.et_pb_column_6')[0].find('h3').find_next('p').get_text()

        store = []
        store.append("https://lotsa.com" + data.find('a').get('href'))
        store.append(store_name)
        store.append(street_add)
        store.append(city)
        store.append(country)
        store.append(pincode)
        store.append("US")
        store.append("<MISSING>")
        store.append(phone)
        store.append("<MISSING>")
        store.append("<MISSING>")
        store.append("<MISSING>")
        store.append(hours)
        return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()