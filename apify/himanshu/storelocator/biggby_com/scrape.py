import csv
import requests
from bs4 import BeautifulSoup
import re
import http.client
import json



def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    base_url = "https://www.biggby.com/"
    conn = http.client.HTTPSConnection("guess.radius8.com")

    addresses = []
   
   
    header = {'User-agent': 'Mozilla/5.0 (Windows; U; Windows NT 5.1; de; rv:1.9.1.5) Gecko/20091102 Firefox/3.5.5',
              'Content-type': 'application/x-www-form-urlencoded'}

   
    data = "https://www.biggby.com/locations/"
    r = requests.get(data, headers=header)
    soup = BeautifulSoup(r.text, "lxml")
    for val in soup.find('div',{'id':'loc-list'}).find_all('marker'):

        locator_domain = base_url
        location_name =  val['name']
        street_address = val['address-one'] +" "+val['address-two']
        city = val['city']
        state =  val['state']
        zip =  val['zip']
        country_code = val['country']
        store_number = val['id']
        phone = ''

        location_type = '<MISSING>'
        latitude = val['lat']
        longitude = val['lng']

        hours_of_operation = ' mon-thurs-open-hour ' + val['mon-thurs-open-hour']+" mon-thurs-close-hour "+val['mon-thurs-close-hour']+" fri-open-hour "+val['fri-open-hour']+" fri-close-hour "+val['fri-close-hour']+" sat-open-hour "+val['sat-open-hour']+" sat-close-hour "+val['sat-close-hour']+" sun-open-hour "+val['sun-open-hour']+" sun-close-hour "+val['sun-close-hour']
        page_url = 'https://www.biggby.com/locations/'
        if street_address in addresses:
            continue
        addresses.append(street_address)
        store = []
        store.append(locator_domain if locator_domain else '<MISSING>')
        store.append(location_name if location_name else '<MISSING>')
        store.append(street_address if street_address else '<MISSING>')
        if "Coming Soon" in store[-1]:
            continue
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
        store.append(page_url if page_url else '<MISSING>')
        yield  store


def scrape():
    data = fetch_data()
    write_output(data)

scrape()    
