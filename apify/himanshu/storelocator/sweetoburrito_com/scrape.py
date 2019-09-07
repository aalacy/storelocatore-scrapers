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
    base_url = "https://sweetoburrito.com/locations/"
    r = requests.get(base_url, headers=headers)
    soup = BeautifulSoup(r.text, "lxml")
    return_main_object = []
    exists = soup.find('main')
    if exists:
        for data in soup.select('.flex_column.av_one_half'):
            location_name = data.select('.av-special-heading-tag')[0].get_text().strip()
            if "," in location_name:
                location_name = data.select('.av-special-heading-tag')[0].get_text().strip().split(',')[0].strip()
                city = location_name
                state = data.select('.av-special-heading-tag')[0].get_text().strip().split(',')[1].strip()
            else:
                if len(data.select('.av-special-heading-tag')[0].find_next('div').get_text()) < 2:
                    city = "<MISSING>"
                    state = "<MISSING>"
                else:
                    city_state = data.select('.av-special-heading-tag')[0].find_next('div').get_text().strip().split(',')
                    city = city_state[0].strip()
                    state = city_state[1].strip()
            if data.select('.iconbox_content_title'):
                phone = data.select('.iconbox_content_title')[0].get_text().strip()[7:]
            else:
                phone = "<MISSING>"
            if "Hours" in data.select('.iconbox_content_container')[0].get_text().strip():
                address = data.select('.iconbox_content_container')[0].get_text().strip()[7:]
                hours_of_operation = address.split(":")[0][:-8]
                street_address = address.split(":")[1].strip()[:-8]
                phone = address.split(":")[3][4:-12]
            else:
                address = data.select('.iconbox_content_container')[0].get_text().strip()
                if "Sun" in address[:4] or "am" in address[:4] or "Mon-" in address[:4]:
                    if "Address" in address.split(":")[0]:
                        hours_of_operation = address.split(":")[0][:-8]
                    else:
                        hours_of_operation = address.split(":")[0]
                    if "AM" in address.split(":")[1][:4] or "pm" in address.split(":")[1][:4]:
                        hours_of_operation = hours_of_operation + " " + address.split(":")[1][:4]
                    street_address = data.select('.iconbox_content_container')[0].get_text().strip().split(":")[1][:-12]
                else:
                    address = data.select('.iconbox_content_container')[0].get_text().strip().split(",")
                    if "Fri" in address[0]:
                        add = address[0].split("83301")
                        street_address = add[0] + " 83301"
                        hours_of_operation = add[1][:-12]
                    else:
                        street_address = address[0]
                        hours_of_operation = "<MISSING>"
            if "Idaho" in location_name:
                street_address = "2090 E 17th street"
            store = []
            store.append(base_url)
            store.append(location_name)
            store.append(street_address)
            store.append(city)
            store.append(state)
            store.append("<MISSING>")
            store.append("US")
            store.append("<MISSING>")
            store.append(phone)
            store.append("Sweeto Burrito")
            store.append("<MISSING>")
            store.append("<MISSING>")
            store.append(hours_of_operation)
            return_main_object.append(store)
        return return_main_object
    else:
        pass

def scrape():
    data = fetch_data()
    write_output(data)
scrape()