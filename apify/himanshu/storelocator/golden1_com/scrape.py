import csv
import requests
from bs4 import BeautifulSoup
import re
import sgzip
import json


def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation",
                         "page_url"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    header = {'User-agent': 'Mozilla/5.0 (Windows; U; Windows NT 5.1; de; rv:1.9.1.5) Gecko/20091102 Firefox/3.5.5',
              'Content-type': 'application/x-www-form-urlencoded'}
    return_main_object = []
    base_url = "https://www.golden1.com/"
    addresses = []
    search = sgzip.ClosestNSearch()
    search.initialize()
    MAX_RESULTS = 100
    MAX_DISTANCE = 10
    addressess =[]
    result_coords = []
    search = sgzip.ClosestNSearch()
    search.initialize()
    data_len = 0
    coords = search.next_coord()
    while coords:
        # print("zip_code === " + str(coords))
        # print("ramiang zip =====" + str(search.current_zip))
        data = "golden1branches=true&golden1homecenters=false&golden1atm=false&sharedbranches=false&sharedatm=false&swlat="+str(coords[0])+"&swlng="+str(coords[1])+"&nelat="+str(coords[0])+"&nelng="+str(coords[1])+"&centerlat="+str(coords[0])+"&centerlng="+str(coords[1])+"&userlat=&userlng="
        location_url = 'https://www.golden1.com/api/BranchLocator/GetLocations'
        try:           
            data = requests.post(location_url, headers=header, data=data).json()
        except:
            continue
        store_number =''
        location_type =''
        if data['locations'] != []:
            data_len =len(data['locations'])
            for json_data in data['locations']:
                street_address = json_data['address']
                city =json_data['city']
                state = json_data['state']
                zipp = json_data['zip']
                hours = json_data['hours']
                location_name = json_data['title']
                latitude =  json_data['lat']
                longitude=  json_data['lng']
                branch =  json_data['switchedToCoOpBranch']
                atm =  json_data['switchedToCoOpATM']
                if branch==True:
                    location_type ="branch"
                if atm==True:
                    location_type = "ATM"
                hours_of_operation = " ".join(list(BeautifulSoup(hours, "lxml").stripped_strings)).replace("\\n","")
                store = []
                result_coords.append((latitude, longitude))
                store.append("https://www.golden1.com")
                store.append(location_name if location_name else '<MISSING>')
                store.append(street_address if street_address else '<MISSING>')
                store.append(city if city else '<MISSING>')
                store.append(state if state else '<MISSING>')
                store.append(zipp if zipp else '<MISSING>')
                store.append("US")
                store.append(store_number if store_number else '<MISSING>')
                store.append( '<MISSING>')
                store.append(location_type if location_type else '<MISSING>')
                store.append(latitude if latitude else '<MISSING>')
                store.append(longitude if longitude else '<MISSING>')
                store.append(hours_of_operation if hours_of_operation else '<MISSING>')
                print(store)
                store.append('<MISSING>')
                if store[2] in addressess:
                    continue
                addressess.append(store[2])
                yield store
        if data_len < MAX_RESULTS:
            # print("max distance update")
            search.max_distance_update(MAX_DISTANCE)
        elif data_len == MAX_RESULTS:
            # print("max count update")
            search.max_count_update(result_coords)
        else:
            raise Exception("expected at most " + str(MAX_RESULTS) + " results")
        coords = search.next_coord()


def scrape():
    data = fetch_data()

    write_output(data)


scrape()
