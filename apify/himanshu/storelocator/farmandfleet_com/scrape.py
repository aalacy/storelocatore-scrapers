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
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    base_url = "https://www.farmandfleet.com/"

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
    # zips  = sgzip.coords_for_radius(50)
    zips = sgzip.for_radius(100)
    header = {'User-agent': 'Mozilla/5.0 (Windows; U; Windows NT 5.1; de; rv:1.9.1.5) Gecko/20091102 Firefox/3.5.5',
              'Content-type': 'application/x-www-form-urlencoded'}
    for coord in zips:
        try:
            data = "query="+str(coord)
            r = requests.post('https://www.farmandfleet.com/store-finder/a/find', headers=header, data=data).json()



            for id,val in enumerate(r):
                locator_domain = base_url
                location_name =  val['textHeader']
                street_address = val['address1']
                city = val['city']
                state =  val['state']
                zip =  val['zip']
                country_code = 'US'
                store_number = val['storeNum']
                phone = ''
                if 'phone' in val:
                    phone = val['phone']
                page_url = base_url+'/stores/'+val['urlAlias']
                latitude = val['latitude']
                longitude = val['longitude']

                # print(val['hours']['tue'][0])
                # exit()
                kk = []

                hours_of_operation = ' monday: ' + val['currentHours']['mondayOpen'] +' : '+ val['currentHours']['mondayClose'] + ' tuesday ' +  val['currentHours']['tuesdayOpen'] + ' : ' + val['currentHours']['tuesdayClose'] + ' wednesday ' + val['currentHours']['wednesdayOpen'] +  ' : ' + val['currentHours']['wednesdayOpen'] + ' thursday ' + val['currentHours']['thursdayOpen'] + ' : ' + val['currentHours']['tuesdayClose'] + ' friday ' + val['currentHours']['fridayOpen'] +  ' : ' + val['currentHours']['fridayClose'] + ' saturday ' + val['currentHours']['saturdayOpen'] + ' : '+ val['currentHours']['saturdayClose'] +'sunday'+val['currentHours']['sundayOpen'] + ' : ' + val['currentHours']['sundayClose']

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
                store.append('<MISSING>')
                store.append(latitude if latitude else '<MISSING>')
                store.append(longitude if longitude else '<MISSING>')
                store.append(hours_of_operation if hours_of_operation else '<MISSING>')
                store.append(page_url if page_url else '<MISSING>')
                print("===", str(store))
                # return_main_object.append(store)
                yield store
            
        except:
            continue
        


    # coord = search.next_coord()


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
