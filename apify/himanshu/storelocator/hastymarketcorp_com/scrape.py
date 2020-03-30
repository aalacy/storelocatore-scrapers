import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
import sgzip



session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    header = {'User-agent': 'Mozilla/5.0 (Windows; U; Windows NT 5.1; de; rv:1.9.1.5) Gecko/20091102 Firefox/3.5.5','Accept':'application/json, text/javascript, */*; q=0.01'}
    return_main_object = []
    base_url = "http://hastymarketcorp.com/"
    zips = sgzip.for_radius(100)
    addresses= []

    r = session.get("http://hastymarketcorp.com/locations-for-sale/browse-listings/?results=500", headers=header)
    soup = BeautifulSoup(r.text, "lxml")
    vk = soup.find_all('h4',{'class':'awpcp-listing-title'})
    for x in vk:

        r = session.get(x.find('a')['href'], headers=header)

        soup = BeautifulSoup(r.text, "lxml")

        locator_domain = base_url
        location_name = soup.find('div',{'class':'awpcp-title'}).text
        street_address = soup.find('div',{'class':'awpcp-title'}).text
        city = soup.find('div',{'class':'showawpcpadpage'}).text.strip().split('\n')[-1].strip().replace('Location:','').strip().split(',')[0].strip()
        state = soup.find('div', {'class': 'showawpcpadpage'}).text.strip().split('\n')[-1].strip().replace('Location:','').strip().split(',')[1].strip()
        country_code = 'CA'
        phone = soup.find('div',{'class':'showawpcpadpage'}).text.strip().split('\n')[-2].replace('Phone:','').strip().split(' ')[0].strip()
        zip = ''
        location_type = 'hastymarketcorp'
        store_number = ''
        latitude = ''
        longitude = ''
        hours_of_operation = ''

        store = []
        store.append(locator_domain if locator_domain else '<MISSING>')
        store.append(location_name if location_name else '<MISSING>')
        store.append(street_address if street_address else '<MISSING>')
        store.append(city if city else '<MISSING>')
        store.append(state if state else '<MISSING>')
        store.append(zip if zip else '<MISSING>')
        store.append(country_code if country_code else '<MISSING>')
        store.append(store_number if store_number else '<MISSING>')
        store.append(phone if phone else '<MISSING>')
        store.append(location_type if location_type else '<MISSING>')
        store.append(latitude if latitude else '<MISSING>')
        store.append(longitude if longitude else '<MISSING>')

        store.append(hours_of_operation if hours_of_operation else '<MISSING>')

        return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()

    write_output(data)


scrape()
