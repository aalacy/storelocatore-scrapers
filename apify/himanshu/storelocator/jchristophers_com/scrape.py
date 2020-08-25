import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json

session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w', encoding="utf-8", newline='') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36'
    }
    base_url = "http://www.jchristophers.com/find-a-j-christophers/"
    r = session.get(base_url, headers=headers, timeout=5)
    soup = BeautifulSoup(r.text, "lxml")
    return_main_object = []
    
    exists = soup.find('div', {'class', 'post-content'})
    if exists:
        for data in exists.findAll('a'):
            if 'ubereats' in data.get('href'):
                continue
            location_name = data.text
            if "@" in data.get('href'):
                latNlongVal = data.get('href').split('@')[1].split(',')
                latitude = latNlongVal[0]
                longitude = latNlongVal[1]
            else:
                latitude = "<MISSING>"
                longitude = "<MISSING>"
            street_address = data.find_next('p').get_text()
            
            city_st_pin = data.find_next('p').find_next('p').get_text().strip()
            
            city_st_pin_val = city_st_pin.split(' ')
            city = " ".join(city_st_pin_val[:-2])[:-1]
            state = city_st_pin_val[-2]
            zipp = city_st_pin_val[-1]
            phone = data.find_next('p').find_next('p').find_next('p').get_text()
            store = []
            store.append(base_url)
            store.append(location_name)
            store.append(street_address)
            store.append(city)
            store.append(state)
            store.append(zipp)
            store.append("US")
            store.append("<MISSING>")
            store.append(phone)
            store.append("J. Christopher's")
            store.append(latitude)
            store.append(longitude)
            store.append("<MISSING>")
            store.append("<MISSING>")
            return_main_object.append(store)
        return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
