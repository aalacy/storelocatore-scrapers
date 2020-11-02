import csv
import requests
from bs4 import BeautifulSoup
import re
import json
import sgzip

def write_output(data):
    with open('data.csv', mode='w', encoding="utf-8") as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)
def fetch_data():
    zips = sgzip.for_radius(100)
    return_main_object = []
    header = {'User-agent' : 'Mozilla/5.0 (Windows; U; Windows NT 5.1; de; rv:1.9.1.5) Gecko/20091102 Firefox/3.5.5'}
    base_url = "https://www.ppgporterpaints.com/"
    addresses = []

    for db in zips:
        loacation_url = 'https://www.ppgporterpaints.com/store-locator/GetRetailerLocations?zip='+str(db)+'&distance=100&streetAddress=&city=&state=Select+State%2FProvince'
        r = requests.get(loacation_url, headers=header).json()
        if r != []:
            for id, vj in enumerate(r):

                locator_domain = base_url

                location_name = str(vj['Name'])
                street_address = vj['StreetAddress']

                if len(vj['CityAddress'].split(',')) == 2:
                    city = vj['CityAddress'].split(',')[0].strip()
                    if len(vj['CityAddress'].split(',')[1].strip().split(' ')) == 2:
                        state = vj['CityAddress'].split(',')[1].strip().split(' ')[0].strip()
                        zip = vj['CityAddress'].split(',')[1].strip().split(' ')[1].strip()
                    else:
                        state =''
                        zip =''
                else:

                    city = ''
                    state = ''
                    zip = ''

                store_number = ''
                country_code = 'US'
                phone = vj['Phone']
                location_type = 'ppgporterpaints'
                latitude = vj['Latitude']
                longitude = vj['Longitude']
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
    return  return_main_object;


def scrape():
    data = fetch_data()
    write_output(data)
scrape()