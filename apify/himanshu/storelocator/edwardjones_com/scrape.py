import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
import sgzip
import time

session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    address = []
    MAX_RESULTS = 50
    MAX_DISTANCE = 100
    search = sgzip.ClosestNSearch()
    search.initialize()
    zip_code = search.next_zip()
    current_results_len =0
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
    }
    while zip_code: 
        result_coords = []
        #print("zip_code === "+zip_code)
        try:
            r = session.get("https://www.edwardjones.com/cgi/findFaByAddress.action?address=" + str(zip_code), headers=headers)
            json_data = r.json()
            current_results_len = len(json_data)
        except:
            continue

        if "error" not in json_data and json_data['multipleLocations'] == False:
            if json_data['faList'] != [] and json_data['faList'] != None:
                for x in json_data['faList']:
                    if x['additionalFaData']['faInfo'] != None:
                        location_name = x['additionalFaData']['faInfo']['convertedName']
                        street_address = x['additionalFaData']['faInfo']['streetAddress']
                        state = x['additionalFaData']['faInfo']['state']
                        city = x['additionalFaData']['faInfo']['city']
                        zipp = x['additionalFaData']['faInfo']['postalCode']
                        store_number = x['additionalFaData']['faInfo']['entityNumber']
                        latitude = x['additionalFaData']['faInfo']['latitude']
                        longitude = x['additionalFaData']['faInfo']['longitude']
                        phone = x['additionalFaData']['faInfo']['phoneNumber']
                        page_url = "https://www.edwardjones.com/cgi/findFaByAddress.action?address=" + str(zip_code)
                        
                        store = []
                        result_coords.append((latitude, longitude))
                        store.append("https://www.edwardjones.com/")
                        store.append(location_name)
                        store.append(street_address if street_address else "<MISSING>")
                        store.append(city)
                        store.append(state)
                        store.append(zipp)   
                        store.append("US")
                        store.append(store_number)
                        store.append(phone)
                        store.append("<MISSING>")
                        store.append(latitude )
                        store.append(longitude )
                        store.append("<MISSING>")
                        store.append(page_url)
                        if store[2] in address:
                            continue     
                        address.append(store[2])
                        yield store
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
