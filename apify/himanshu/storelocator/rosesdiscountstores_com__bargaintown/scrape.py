import csv
import requests
from bs4 import BeautifulSoup
import re
import json

def write_output(data):
    with open('data.csv', mode='w', encoding="utf-8") as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        for row in data:
            writer.writerow(row)
def fetch_data():
        
        addresses = []
        return_main_object = []
        header = {'User-agent': 'Mozilla/5.0 (Windows; U; Windows NT 5.1; de; rv:1.9.1.5) Gecko/20091102 Firefox/3.5.5'}
        base_url = 'https://www.rosesdiscountstores.com/#bargaintown'
        location_url  = 'https://api.zenlocator.com/v1/apps/app_vfde3mfb/locations/search?northeast=69.659042%2C70.11417&southwest=-77.464808%2C-180'

        r = requests.get(location_url, headers=header).json()
        for id,vj in enumerate(r['locations']):
            locator_domain = base_url
            location_name = vj['name']
            # if ''
            street_address = vj['address'].split(',')[0].strip()
            city = vj['city']
            state = vj['region']
            zip = vj['postcode']
            store_number = vj['importLogId']
            country_code = vj['countryCode']
            try:
                phone = vj['contacts']['con_wg5rd22k']['text']
            except:
                phone = "<MISSING>"
            location_type = '<MISSING>'
            latitude = vj['lat']
            longitude = vj['lng']
            if street_address in addresses:
                continue
            addresses.append(street_address)
            if vj['hours'] != "hrs_ywfef43p":
                if vj['hours'] == "hrs_a4db656x":
                    hours_of_operation = '<MISSING>'
                else :
                    if vj['hours']:
                        hours_of_operation1 = vj['hours']
                        ki = (hours_of_operation1['hoursOfOperation'])
                        hours_of_operation = ("sun"+" - "+ki['sun']+","+"mon"+" - "+ki['mon']+","+"tue"+" - "+ki['tue']+","+"wed"+" - "+ki['wed']+","+"thu"+" - "+ki['thu']+","+"fri"+" - "+ki['fri']+","+"sat"+" - "+ki['sat'])
            else:
                hours_of_operation = '<MISSING>'
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
            store.append('<MISSING>')
            # print('===', str(store))
            return_main_object.append(store)
        return return_main_object
def scrape():
    data = fetch_data()
    write_output(data)
scrape()
