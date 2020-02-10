import csv
import requests
from bs4 import BeautifulSoup
import re
import json
import sgzip


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
    header = {'User-agent': 'Mozilla/5.0 (Windows; U; Windows NT 5.1; de; rv:1.9.1.5) Gecko/20091102 Firefox/3.5.5'}
    return_main_object = []
    base_url = "https://www.bossplow.com/"
    addresses = []
    zips = sgzip.for_radius(100)
    for x in zips:
        try:
            r = requests.get("https://www.bossplow.com/en/locator?countryCode=US&postalCode="+x+"&resultType=Dealer", headers=header)
        except:
            continue
        soup = BeautifulSoup(r.text, "lxml")
        for zx in  soup.findAll('div',{'class':'dealer-panel-primary'}):
                locator_domain = base_url
                location_name = zx.find('a',{'class':'dealer-marker'}).text

                if len(zx.find('address').text.strip().replace('\r','').split('\n')) == 5:
                    street_address = zx.find('address').text.strip().replace('\r','').split('\n')[0].strip()
                    city = zx.find('address').text.strip().replace('\r', '').split('\n')[1].strip().split(',')[0].strip()
                    state =  zx.find('address').text.strip().replace('\r', '').split('\n')[1].strip().split(',')[1].strip().split(' ')[0].strip()
                    zip =  zx.find('address').text.strip().replace('\r', '').split('\n')[1].strip().split(',')[1].strip().split(' ')[1].strip()
                    country_code = zx.find('address').text.strip().replace('\r', '').split('\n')[1].strip().split(',')[1].strip().split(' ')[2].strip()
                    store_number = '';
                    phone = zx.find('address').text.strip().replace('\r','').split('\n')[2].replace('Phone:','').strip()
                    location_type = 'bossplow'
                    latitude = ''
                    longitude = ''
                    hours_of_operation = ''

                    if street_address in addresses:
                        continue
                    addresses.append(street_address)

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
