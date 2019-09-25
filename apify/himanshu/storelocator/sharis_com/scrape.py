import csv
import requests
from bs4 import BeautifulSoup
import re
import http.client
import sgzip
import json
import  pprint


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
    base_url = "https://sharis.com/"

    conn = http.client.HTTPSConnection("guess.radius8.com")
    headers = {
        'authorization': "R8-Gateway App=shoplocal, key=guess, Type=SameOrigin",
        'cache-control': "no-cache"
    }

    addresses = []

    search = sgzip.ClosestNSearch()
    search.initialize()
    # zips = sgzip.coords_for_radius(100)
    # coord = search.next_coord()
    # zips  = sgzip.coords_for_radius(50)
    zips = sgzip.for_radius(200)
    header = {'User-agent': 'Mozilla/5.0 (Windows; U; Windows NT 5.1; de; rv:1.9.1.5) Gecko/20091102 Firefox/3.5.5',
              'Content-type': 'application/x-www-form-urlencoded'}
    for coord in zips:


        r = requests.post("https://sharis.com/wp-admin/admin-ajax.php?address="+str(coord)+"&formdata=nameSearch%3D%26addressInput%3D97008%26addressInputCity%3D%26addressInputState%3D%26addressInputCountry%3D%26ignore_radius%3D0&radius=200&tags=&action=csl_ajax_search", headers=header).json()

        # print("response ===", str(r['response']))
        for val in r['response']:

            locator_domain = base_url
            location_name =  val['name']
            street_address = val['address']
            city = val['city']
            state =  val['state']
            zip =  val['zip']
            country_code = 'US'
            store_number = val['id']
            phone = val['phone']
            if 'phone' in val:
                phone = val['phone']
            location_type = ''
            latitude = val['lat']
            longitude = val['lng']

            hours_of_operation = val['hours'].replace('&lt;br/&gt;',' ')

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
            # print("===", str(store))
            # return_main_object.append(store)
            yield store


    # coord = search.next_coord()


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
