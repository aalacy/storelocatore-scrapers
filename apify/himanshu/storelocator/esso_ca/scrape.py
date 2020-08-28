import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
import sgzip

session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w',newline="") as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    search = sgzip.ClosestNSearch()
    search.initialize(country_codes= ["CA"])
    MAX_RESULTS = 250
    MAX_DISTANCE = 25
    current_result_len = 0
    coords = search.next_coord()

    addresses = []

    while coords:
        result_coords = []
        #print("remaining zipcodes: " + str(search.zipcodes_remaining()))
        # print(coords[0],coords[1])
        base_url = "https://www.esso.ca/en-CA/api/locator/Locations?Latitude1="+str(coords[0])+"&Latitude2="+str(coords[0]+1)+"&Longitude1="+str(coords[1])+"&Longitude2="+str(coords[1]+1)+"&DataSource=RetailGasStations&Country=CA"
        # base_url = "https://www.esso.ca/en/api/v1/Retail/retailstation/GetStationsByBoundingBox?Latitude1=16.698659791445607&Latitude2=36.22597707315531&Longitude1=-76.07080544996313&Longitude2=-119.57666482496313"
        r = session.get(base_url).json()
        current_result_len = len(r)
        for esso in r:
            store = []
            result_coords.append((esso['Latitude'],esso['Longitude']))
            store.append("https://www.esso.ca")
            store.append(esso['DisplayName'])
            if "AddressLine2" not in esso:
                store.append(esso['AddressLine1'])
            else:
                store.append(esso['AddressLine1'] + " "+esso['AddressLine2'])
            try:
                store.append(esso['City'])
            except:
                store.append("MISSING")
            try:
                store.append(esso['StateProvince'])
            except:
                store.append("<MISSING>")
            try:
                store.append(esso['PostalCode'])
            except:
                store.append("<MISSING>")
            if esso['Country']=="Canada":
                store.append("CA")
            else:
                store.append(esso['Country'])
            store.append(esso["LocationID"])
            if esso['Telephone']:
                store.append(esso['Telephone'])
            else:
                store.append("<MISSING>")
            store.append(esso["EntityType"])
            store.append(esso['Latitude'])
            store.append(esso['Longitude'])
            try:
                store.append(esso['WeeklyOperatingHours'].replace('<br/>',','))
            except:
                store.append("<MISSING>")
            page_url = "https://www.esso.ca/en-ca/find-station/"+esso['City'].lower().strip()+"-"+esso['StateProvince'].lower().strip()+"-esso-"+esso["LocationID"]
            store.append(page_url)
            if (str(store[2])+str(store[-1])) in addresses:
                continue
            addresses.append(str(store[2])+str(store[-1]))
            store = [str(x).encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]
            yield store
            #print(store)
        if current_result_len < MAX_RESULTS:
            # print("max distance update")
            search.max_distance_update(MAX_DISTANCE)
        elif current_result_len == MAX_RESULTS:
            # print("max count update")
            search.max_count_update(result_coords)
        else:
            raise Exception("expected at most " + str(MAX_RESULTS) + " results")
        coords = search.next_coord()
def scrape():
    data = fetch_data()
    write_output(data)

scrape()
