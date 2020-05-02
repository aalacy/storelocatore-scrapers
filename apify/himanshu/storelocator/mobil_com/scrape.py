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
    search.initialize(country_codes= ["US"])
    MAX_RESULTS = 250
    MAX_DISTANCE = 25
    current_result_len = 0
    coords = search.next_coord()

    addresses = []

    while coords:
        result_coords = []
        # print("remaining zipcodes: " + str(len(search.zipcodes)))
        # print(coords[0],coords[1])
        base_url = "https://www.exxon.com/en/api/locator/Locations?Latitude1="+str(coords[0])+"&Latitude2="+str(coords[0]+1)+"&Longitude1="+str(coords[1])+"&Longitude2="+str(coords[1]+1)+"&DataSource=RetailGasStations&Country=US"
        r = session.get(base_url).json()
        current_result_len = len(r)
        for exxon in r:
            store = []
            result_coords.append((exxon['Latitude'],exxon['Longitude']))
            store.append("https://www.mobil.com")
            store.append(exxon['DisplayName'])
            if "AddressLine2" not in exxon:
                store.append(exxon['AddressLine1'])
            else:
                store.append(exxon['AddressLine1'] + " "+exxon['AddressLine2'])
            try:
                store.append(exxon['City'])
            except:
                store.append("MISSING")
            try:
                store.append(exxon['StateProvince'])
            except:
                store.append("<MISSING>")
            try:
                store.append(exxon['PostalCode'])
            except:
                store.append("<MISSING>")
            if exxon['Country']=="Canada":
                store.append("CA")
            else:
                store.append(exxon['Country'])
            store.append(exxon["LocationID"])
            if exxon['Telephone']:
                phone_list = re.findall(re.compile(".?(\(?\d{3}\D{0,3}\d{3}\D{0,3}\d{4}).?"), str(exxon['Telephone']))
                if phone_list:
                    store.append(phone_list[0])
                else:
                    store.append("<MISSING>")
                
            else:
                store.append("<MISSING>")
            loc_slug = " ".join(re.findall("[a-zA-Z0-9]+", exxon["DisplayName"])).lower().replace(" ","-").strip()
            # print(loc_slug)
            page_url = "https://www.exxon.com/en/find-station/"+exxon['City'].replace(" ","-").lower().strip()+"-"+exxon['StateProvince'].lower().strip()+"-"+str(loc_slug)+"-"+exxon["LocationID"]
            r_loc = session.get(page_url)
            soup_loc = BeautifulSoup(r_loc.text,"lxml")
            loc_type = soup_loc.find("div",class_="row station-locator-details").find("img")["src"]
            if "exxon" in loc_type:
                location_type = "exxon"
                store.append(location_type)
            elif "mobil" in loc_type:
                location_type="mobil"
                store.append(location_type)
            else:
                continue
            store.append(exxon['Latitude'])
            store.append(exxon['Longitude'])
            try:
                store.append(exxon['WeeklyOperatingHours'].replace('<br/>',','))
            except:
                store.append("<MISSING>")
            store.append(page_url)
            duplicate = str(store[1])+ " " +str(store[2])+" "+str(store[-3])+" "+str(store[-4]) +" "+str(store[-5])+" "+str(store[-1])
            if str(duplicate) in addresses:
                continue
            addresses.append(str(duplicate))
            store = [str(x).encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]
            yield store
            # print(store)
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
