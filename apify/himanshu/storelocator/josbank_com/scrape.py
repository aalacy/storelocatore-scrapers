import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
import sgzip
from sglogging import SgLogSetup
logger = SgLogSetup().get_logger('josbank_com')
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
    addresses = []
    search = sgzip.ClosestNSearch()
    search.initialize()
    MAX_RESULTS = 200
    MAX_DISTANCE = 100
    current_results_len = 0     # need to update with no of count.
    zip_code = search.next_zip()
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
    }
    base_url = "https://www.josbank.com/"
    while zip_code:
        result_coords = []
        # logger.info("zip_code === "+zip_code)
        location_url = "https://www.josbank.com/sr/search/resources/store/13452/storelocator/byProximity?catalogId=14052&langId=-24&radius=500&zip="+str(zip_code)+"&city=&state=&brand=JAB&profileName=X_findStoreLocatorWithExtraFields"
        try:
            r = session.get(location_url,headers=headers)
        except:
            continue
        json_data = r.json()
        if json_data != [] and json_data != None:
            if "DocumentList" in json_data:
                if json_data['DocumentList'] != [] and json_data['DocumentList'] != None:
                    current_results_len = len(json_data['DocumentList'])
                    for i in json_data['DocumentList']:
                        location_name = i['storeName']
                        street_address = i['address1_ntk']
                        city = i['city_ntk']
                        state = i['state_ntk']
                        zipp = i['zipcode_ntk']
                        store_number = i['stloc_id']
                        phone = i['phone_ntk']
                        latitude = i['latlong'].split(',')[0]
                        longitude = i['latlong'].split(',')[1]
                        hours_of_operation = i['working_hours_ntk'].replace('<br>',', ').replace(", TUE",", TUE ").replace("SUN","SUN ").replace(", MON",", MON ").replace(", SAT",", SAT ").replace(", FRI",", FRI ").replace(", WED",", WED ").replace(", THU",", THU ").replace("-"," - ")
                        page_url = "https://www.josbank.com/store-locator/"+str(city).lower()+"-"+str(state).lower()+"-"+str(store_number)+"?address="+str(zip_code)+"%20%2C"
                        page_url = page_url.replace(" ","-").replace("fort%20worth","fort-worth")
                        result_coords.append((latitude, longitude))
                        store = []
                        store.append(base_url)
                        store.append(location_name)
                        store.append(street_address)
                        store.append(city)
                        store.append(state)
                        store.append(zipp)
                        store.append("US")
                        store.append(store_number) 
                        store.append(phone)
                        store.append("<MISSING>")
                        store.append(latitude)
                        store.append(longitude)
                        store.append(hours_of_operation)
                        store.append(page_url)
                        if store[2] in addresses:
                            continue
                        addresses.append(store[2])  
                        yield store
        if current_results_len < MAX_RESULTS:
            # logger.info("max distance update")
            search.max_distance_update(MAX_DISTANCE)
        elif current_results_len == MAX_RESULTS:
            # logger.info("max count update")
            search.max_count_update(result_coords)
        else:
            raise Exception("expected at most " + str(MAX_RESULTS) + " results")
        zip_code = search.next_zip()
def scrape():
    data = fetch_data()
    write_output(data)
scrape()
