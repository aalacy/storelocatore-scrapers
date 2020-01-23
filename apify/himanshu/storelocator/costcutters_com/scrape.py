import csv
import requests
from bs4 import BeautifulSoup
import re
import json
import sgzip

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    addresses = []
    base_url = "https://www.signaturestyle.com"
    search = sgzip.ClosestNSearch()
    search.initialize(country_codes= ["US","CA"])
    MAX_RESULTS = 100
    MAX_DISTANCE = 100
    coord = search.next_coord()
    headers = {
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36',
    }
    while coord:
        result_coords = []
        x = coord[0]
        y = coord[1]
    
    
        r = requests.get("https://info3.regiscorp.com/salonservices/siteid/100/salons/searchGeo/map/"+str(x)+"/"+str(y)+"/0.5/0.5/true", headers=headers).json()
        # print()
        for i in r['stores']:
            location_name = i['title']
            street_address = i['subtitle'].split(',')[0]
            city = i['subtitle'].split(',')[1].strip()
            state = i['subtitle'].split(',')[-1].split(" ")[1]
            zipp = i['subtitle'].split(',')[-1].split(" ")[2]
            if len(zipp)==5:
                country_code="US"
            else:
                country_code="CA"
            store_number = i['storeID']
            latitude = i['latitude']
            longitude = i['longitude']
            phone = i['phonenumber']
            hours = ''
            for time in  i['store_hours']:
                hours+= time['days']+" "+time['hours']['open']+"-"+time['hours']['close']
            hours = hours
            page_url = "https://www.signaturestyle.com/locations/"+str(state.lower())+"/"+str(city.lower())+"/cost-cutters-"+str(location_name.lower().replace(" ","-"))+"-haircuts-"+str(store_number)+".html"
            

            result_coords.append((latitude,longitude))
            store=[]
            store.append(base_url)
            store.append(location_name)
            store.append(street_address)
            store.append(city)
            store.append(state)
            store.append(zipp)
            store.append(country_code)
            store.append(store_number)
            store.append(phone)
            store.append("<MISSING>")
            store.append(latitude)
            store.append(longitude)
            store.append(hours)
            store.append(page_url)
            if store[2] in addresses:
                continue
            addresses.append(store[2])
            store = [x.encode('ascii', 'ignore').decode('ascii').strip() if type(x) == str else x for x in store]
            yield store
            # print("data===="+str(store))
            # print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~`")


        if len(r['stores']) < MAX_RESULTS:
            # print("max distance update")
            search.max_distance_update(MAX_DISTANCE)
        elif len(r['stores']) == MAX_RESULTS:
            # print("max count update")
            search.max_count_update(result_coords)
        else:
            raise Exception("expected at most " + str(MAX_RESULTS) + " results")
        coord = search.next_coord()


def scrape():
    data = fetch_data()
    write_output(data)

scrape()
