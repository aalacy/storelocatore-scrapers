import csv
import requests
import http.client
from bs4 import BeautifulSoup
import re
import json
import sgzip

def write_output(data):
    with open('data.csv', mode='w', encoding="utf-8") as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)
def fetch_data():
        zips = sgzip.for_radius(100)
        lat_lon = sgzip.coords_for_radius(200)
        addresses = []
        return_main_object = []
        for z in lat_lon:
            try:
                base_url = "www.gamestop.com"
                conn = http.client.HTTPSConnection("www.gamestop.com")
                location_url = "/on/demandware.store/Sites-gamestop-us-Site/default/Stores-FindStores?radius=500&radius=500&lat="+str(z[0])+"&lat="+str(z[0])+"&long="+str(z[1])+"&long="+str(z[1])
                conn.request("GET",location_url)

                res = conn.getresponse()
                data = res.read()

                get_deata = json.loads(data.decode("utf-8"))



                if 'stores' in get_deata:

                    for key,vj in enumerate(get_deata['stores']):
                        locator_domain = base_url   
                        location_name = vj['name']
                        street_address = vj['address1']
                        city = vj['city']
                        state = vj['stateCode']
                        zip =  vj['postalCode']
                        store_number = vj['ID']
                        country_code = vj['countryCode']
                        phone = vj['phone']
                        location_type = '<MISSING>'
                        latitude = vj['latitude']
                        longitude = vj['longitude']

                        if street_address in addresses:
                            continue
                        addresses.append(street_address)

                        hours_of_operation = vj['storeHours']


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
                        print("====",str(store))

                        yield store
            except:
                continue


        return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)
scrape()
