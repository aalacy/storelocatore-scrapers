import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
import sgzip
session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w',encoding="utf-8") as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)
def fetch_data():
    MAX_RESULTS = 100
    MAX_DISTANCE = 100
    search = sgzip.ClosestNSearch()
    search.initialize(country_codes=['US'])
    zip_code = search.next_zip()
    current_results_len = 0
    adressess = []
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
    }
    while zip_code:
        result_coords =[]
        # print("zip_code === "+zip_code)
        # print("remaining zipcodes: " + str(len(search.zipcodes)))
        r = session.get("https://www.thelittleclinic.com/tlc/api/clinic/search?freeFormAddress="+ str(zip_code) +"&maxResults=300&pageSize=500",headers=headers)
        json_data = r.json()
        j = (json_data['results'])
        for i in j :
            store = []
            store.append("https://www.thelittleclinic.com/")
            store.append(i['legalName'])
            store.append(i['address']['addressLine1'])
            store.append(i['address']['city'])
            store.append(i['address']['stateCode'])
            store.append(i['address']['zip'])
            store.append(i['address']['countryCode'])
            store.append(i['storeNumber'])
            store.append(i['phoneNumber'])
            store.append(i['banner'])
            store.append(i['latitude'])
            store.append(i['longitude'])
            store.append("<INACCESSBLE>")
            store.append("https://www.thelittleclinic.com/scheduler/tlc/location/"+str(i['clinicId']))
            if store[2] in adressess:
                continue
            adressess.append(store[2])
            store = [str(x).encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]
            yield store
        if current_results_len < MAX_RESULTS:
            search.max_distance_update(MAX_DISTANCE)
        elif current_results_len == MAX_RESULTS:
            search.max_count_update(result_coords)
        else:
            raise Exception("expected at most " + str(MAX_RESULTS) + " results") 
        zip_code = search.next_zip()
def scrape():
    data = fetch_data()
    write_output(data)
scrape()
