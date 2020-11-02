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
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36'
    }
    base_url = "http://www.drivenstyle.com/locations/"
    r = session.get(base_url, headers=headers)
    soup = BeautifulSoup(r.text, "lxml")
    return_main_object = []
    exists = soup.find('ul', {'class', 'states__list'})
    if exists:
        for links in exists.findAll('a'):
            city = links.get_text()
            url = "http://www.drivenstyle.com" + links.get('href')
            detail_url = session.get(url, headers=headers)
            detail_soup = BeautifulSoup(detail_url.text, "lxml")
            detail_exists = detail_soup.find('div', {'class', 'location__inner'})
            if detail_exists:
                for data in detail_exists.findAll('article'):
                    location_name = data.find('h3').get_text()
                    phone = data.find('a').find_next('a').get_text()
                    address = data.find('address').get_text().strip().split(',')
                    street_address = address[0]
                    state = address[1].strip().split(' ')[0].strip()
                    zip = address[1].strip().split(' ')[1].strip()
                    store = []
                    store.append('http://www.drivenstyle.com/')
                    store.append(location_name)
                    store.append('<MISSING>')
                    store.append(city)
                    store.append(state)
                    store.append(zip)
                    store.append("US")
                    store.append("<MISSING>")
                    store.append(phone)
                    store.append("<MISSING>")
                    store.append("<MISSING>")
                    store.append("<MISSING>")
                    store.append("<MISSING>")
                    store.append(url)
                    return_main_object.append(store)
            else:
                pass
    else:
        pass
    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)
scrape()