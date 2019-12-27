import csv
import sys

import requests
from bs4 import BeautifulSoup
import re
import json
import sgzip


def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',',
                            quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    # header = {'User-agent': 'Mozilla/5.0 (Windows; U; Windows NT 5.1; de; rv:1.9.1.5) Gecko/20091102 Firefox/3.5.5','Accept':'application/json, text/javascript, */*; q=0.01'}
    return_main_object = []
    base_url = "https://www.dunkindonuts.com/"
    zips = sgzip.for_radius(50)
    addresses = []

    for z in zips:
        #print(z)

        try:

            r = requests.get("https://www.mapquestapi.com/search/v2/radius?callback=jQuery22408729727990432037_1568814338463&key=Gmjtd%7Clu6t2luan5%252C72%253Do5-larsq&origin=" + str(z) + ""
                             "&units=m&maxMatches=4000&radius=100&hostedData=mqap.33454_DunkinDonuts&ambiguities=ignore&_=1568814338464")

            soup = BeautifulSoup(r.text, "lxml")
            ck = soup.text.split(
                'jQuery22408729727990432037_1568814338463(')[1].split(');')[0]
            data_json = json.loads(ck)
            for x in data_json['searchResults']:
                vj = x['fields']

                locator_domain = base_url

                location_name = 'Dunkin Donuts'
                street_address = vj['address'].strip()

                city = vj['city'].strip()
                state = vj['state'].strip()
                zip = vj['postal'].strip()

                store_number = vj['recordid']
                country_code = vj['country'].strip()
                if vj['phonenumber'] == '--':
                    phone = ''
                else:
                    phone = vj['phonenumber'].strip()
                location_type = 'dunkindonuts'
                latitude = vj['lat']
                longitude = vj['lng']

                if street_address in addresses:
                    continue
                addresses.append(street_address)

                hours_of_operation = ' mon ' + vj['mon_hours'] + '  tue' + vj['tue_hours'] + ' wed ' + vj['wed_hours'] + \
                    ' thu ' + vj['thu_hours'] + ' fri ' + vj['fri_hours'] + \
                    ' sat ' + vj['sat_hours'] + ' sun ' + vj['sun_hours']
                page_url = "https://www.dunkindonuts.com/en/locations?location=" + \
                    str(z)

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

                store.append(
                    hours_of_operation if hours_of_operation else '<MISSING>')
                store.append(page_url if page_url else "<MISSING>")

                # print("data == " + str(store))
                # print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~`")
                return_main_object.append(store)
        except:
            continue
    return return_main_object


def scrape():
    data = fetch_data()

    write_output(data)


scrape()
