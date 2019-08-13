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
    base_url = "https://nynypizzeria.com/locations/"
    r = requests.get(base_url, headers=headers)
    soup = BeautifulSoup(r.text, "lxml")
    return_main_object = []
    address = []
    data = soup.findAll('div', {'class', 'featured_block_text'})
    for values in data:
        data_val= values.select('.cmsmasters_heading_wrap.cmsmasters_heading_align_center')[0].find('h3').get_text()
        pin_st_city_loc = data_val.split(' ')
        if pin_st_city_loc[-1].isdigit():
            location_name = (' ').join(data_val.split(' ')[:-3]).strip()
            street_address = (' ').join(data_val.split(' ')[:-3]).strip()
            city = pin_st_city_loc[-3][:-1].strip()
            state = pin_st_city_loc[-2].strip()
            zip = pin_st_city_loc[-1].strip()

        phone_number = values.select('.cmsmasters_heading_wrap.cmsmasters_heading_align_center')[1].find('h3').get_text()
        if not phone_number.isspace():
            phone = phone_number.strip()[5:]
        store = []	
        store.append(base_url)
        store.append(location_name)
        store.append(street_address)
        store.append(city)
        store.append(state)
        store.append(zip)
        store.append("US")
        store.append("<MISSING>")
        store.append(phone)
        store.append("New York Pizza")
        store.append("<INACCESSIBLE>")
        store.append("<INACCESSIBLE>")
        store.append("<MISSING>")
        return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)
scrape()
