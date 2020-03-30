import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
import sgzip
import time



session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w', encoding="utf-8") as output_file:
        writer = csv.writer(output_file, delimiter=',',
                            quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    return_main_object = []
    addresses = []
    search = sgzip.ClosestNSearch()
    search.initialize(include_canadian_fsas = True)
    MAX_RESULTS = 10
    MAX_DISTANCE = 50
    current_results_len = 0  # need to update with no of count.
    zip_code = search.next_zip()


    headers = {
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36',
        "accept": "application/json, text/javascript, */*; q=0.01",
        # "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    }

    # it will used in store data.
    locator_domain = "https://www.lequipeur.com/"
    location_name = ""
    street_address = "<MISSING>"
    city = "<MISSING>"
    state = "<MISSING>"
    zipp = "<MISSING>"
    country_code = ""
    store_number = "<MISSING>"
    phone = "<MISSING>"
    location_type = "lequipeur"
    latitude = "<MISSING>"
    longitude = "<MISSING>"
    raw_address = ""
    hours_of_operation = "<MISSING>"
    page_url = "<MISSING>"

    while zip_code:
        result_coords = []
        try:
            r= session.get('https://www.lequipeur.com/services-rest/marks/stores?code=&productIds=&locale=en&location=+'+str(zip_code),headers = headers)
            json_data = r.json()
        except:
            continue

        first_key = list(json_data.keys())[0]
        if first_key == 'results':
            # print(json_data['results'])
            # print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
            for z in json_data['results']:
                store_number = z['name']
                location_name = z['title']
                street_address = z['address']['formattedAddress']
                city = z['address']['town']
                state = z['address']['province']
                zipp = z['address']['postalCode']
                phone = z['address']['phone']
                latitude = z['latitude']
                longitude = z['longitude']
                page_url = z['storeLink']
                hours_of_operation = z['workingTime']
                country_code = z['address']['countryIsoCode']

                result_coords.append((latitude, longitude))
                if street_address in addresses:
                    continue

                addresses.append(street_address)

                store = []
                store.append(locator_domain if locator_domain else '<MISSING>')
                store.append(location_name if location_name else '<MISSING>')
                store.append(street_address if street_address else '<MISSING>')
                store.append(city if city else '<MISSING>')
                store.append(state if state else '<MISSING>')
                store.append(zipp if zipp else '<MISSING>')
                store.append(country_code if country_code else '<MISSING>')
                store.append(store_number if store_number else '<MISSING>')
                store.append(phone if phone else '<MISSING>')
                store.append(location_type if location_type else '<MISSING>')
                store.append(latitude if latitude else '<MISSING>')
                store.append(longitude if longitude else '<MISSING>')

                store.append(hours_of_operation if hours_of_operation else '<MISSING>')
                store.append(page_url if page_url else '<MISSING>')
                # print("data===="+str(store))
                # print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
                # yield store

                return_main_object.append(store)
        if current_results_len < MAX_RESULTS:
            # print("max distance update")
            search.max_distance_update(MAX_DISTANCE)
        elif current_results_len == MAX_RESULTS:
            # print("max count update")
            search.max_count_update(result_coords)
        else:
            raise Exception("expected at most " + str(MAX_RESULTS) + " results")

        zip_code = search.next_zip()
    return return_main_object




def scrape():
    data = fetch_data()
    write_output(data)


scrape()
