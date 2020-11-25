import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
import sgzip
import time
session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w', encoding="utf-8", newline='') as output_file:
        writer = csv.writer(output_file, delimiter=',',
                            quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
  
    addresses = []
    search = sgzip.ClosestNSearch() # TODO: OLD VERSION [sgzip==0.0.55]. UPGRADE IF WORKING ON SCRAPER!
    search.initialize(country_codes=['CA'])
    MAX_RESULTS = 100
    MAX_DISTANCE = 50
    current_results_len = 0     # need to update with no of count.
    zip_code = search.next_zip()


    headers = {
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36',
        "accept": "application/json, text/javascript, */*; q=0.01",
        # "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    }

    
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
    hours_of_operation = "<MISSING>"
    page_url = "<MISSING>"

    while zip_code:
        result_coords = []
        url = "https://api.lequipeur.com/hy/v1/lequipeur/storelocators/near"
        
        querystring = {"location":str(zip_code),"pageSize":"20"}
        try:
            json_data = session.get(url, headers=headers, params=querystring).json()
            current_results_len = len(json_data['storeLocatorPageData']['results'])
            for z in json_data['storeLocatorPageData']['results']:
                store_number = z['name']
                location_name = z['displayName']
                street_address = z['address']['line1']
                if z['address']['line2']:
                    street_address += " " + z['address']['line2']
                city = z['address']['town']
                state = z['address']['province']
                zipp = z['address']['postalCode']
                phone = z['address']['phone']
                latitude = z['geoPoint']['latitude']
                longitude = z['geoPoint']['longitude']
                page_url = "https://www.lequipeur.com/en/stores/" + z['urlLocalized'][0]['value'].split("/")[-1]
                hours_of_operation = z['workingHours']
                country_code = z['address']['country']['isocode']
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
                store.append(re.sub(r'\s+'," ",hours_of_operation) if hours_of_operation else '<MISSING>')
                store.append(page_url if page_url else '<MISSING>')
                yield store
        except:
            pass

        if current_results_len < MAX_RESULTS:
            # print("max distance update")
            search.max_distance_update(MAX_DISTANCE)
        elif current_results_len == MAX_RESULTS:
            # print("max count update")
            search.max_count_update(result_coords)
        else:
            raise Exception("expected at most " + str(MAX_RESULTS) + " results")
        zip_code = search.next_zip()
def scrape():
    data = fetch_data()
    write_output(data)
scrape()
