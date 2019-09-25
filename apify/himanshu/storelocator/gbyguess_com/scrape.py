import csv
import requests
from bs4 import BeautifulSoup
import re
import http.client
import sgzip
import json


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
    base_url = "https://www.gbyguess.com/"

    conn = http.client.HTTPSConnection("guess.radius8.com")
    headers = {
        'authorization': "R8-Gateway App=shoplocal, key=guess, Type=SameOrigin",
        'cache-control': "no-cache"
    }

    addresses = []

    search = sgzip.ClosestNSearch()
    search.initialize()
    # zips = sgzip.coords_for_radius(100)
    coord = search.next_coord()
    zips  = sgzip.coords_for_radius(50)
    # location_url = 'https://guess.radius8.com/api/v1/streams/stores?lat='+str(x)+'&lng='+str(y)+'&radius=1000&units=MI&limit=50&divisions=g%20by%20guess&_ts=1569321866194'
    for coord in zips:
        x = coord[0]
        y = coord[1]
        conn.request("GET",
                     "/api/v1/streams/stores?lat="+str(x)+"&lng="+str(y)+"&radius=1000&units=MI&limit=200&divisions=g%20by%20guess&_ts=1569321866194",
                     headers=headers)
        # conn.request("GET",
        #              "/api/v1/streams/stores?lat=40.7226698&lng=-73.51818329999998&radius=1000&units=MI&limit=200&divisions=g%20by%20guess&_ts=1569321866194",
        #              headers=headers)
        res = conn.getresponse()
        data = res.read()
        json_data  = json.loads( data.decode("utf-8"))

        for id,val in enumerate(json_data['results']):
            locator_domain = base_url
            location_name =  val['name']
            street_address = val['address']['address1']
            city = val['address']['city']
            state = ''
            if 'state' in val['address']:
                state =  val['address']['state']
            zip =  val['address']['postal_code']
            country_code = val['address']['country']
            store_number = val['store_code']
            phone = ''
            if 'phone' in val:
                phone = val['contact_info']['phone']
            location_type = 'guess'
            latitude = val['geo_point']['lat']
            longitude = val['geo_point']['lng']

            # print(val['hours']['tue'][0])
            # exit()
            kk = []
            for x in val['hours']:
                kk.append(x + "=" + val['hours'][x][0][:2]+':'+val['hours'][x][0][2:4] +" AM to PM " + val['hours'][x][1][:2]+':'+val['hours'][x][1][2:4])

            hours_of_operation = ' '.join(kk)

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
            print("===", str(store))
            # return_main_object.append(store)
            yield store


    # coord = search.next_coord()


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
