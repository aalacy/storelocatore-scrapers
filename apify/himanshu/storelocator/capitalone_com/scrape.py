import csv
from bs4 import BeautifulSoup
import re
import json
import sgzip
from sgrequests import SgRequests
session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w',newline="") as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url","operating_info"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
        "X-Requested-With": "XMLHttpRequest",
        "content-type": "application/json;charset=UTF-8",
        "Accept": "application/json, text/plain, */*"
    }
    # """  BRANCHLOC  CAFELOC"""
    addresses = []
    search = sgzip.ClosestNSearch()
    search.initialize()
    MAX_RESULTS = 100
    MAX_DISTANCE = 50.0
    coord = search.next_coord()
    while coord:
        result_coords = []
        # print("remaining zipcodes: " + str(len(search.zipcodes)))
        x = coord[0]
        y = coord[1]
        # print('Pulling Lat-Long %s,%s...' % (str(x), str(y)))
        r_data = '{"lat":' + str(x) + ',"lng":' + str(y) + ',"radius":50,"services":[],"resType":["BRANCHLOC","CAFELOC"]}'
        try:
            r = session.post("https://locations.capitalone.com/resourcelocator/location/resources/",headers=headers,data=r_data)
        except:
            pass
        data = r.json()["resourceList"]
        for store_data in data:
            lat = store_data["latitude"]
            lng = store_data["longitude"]
            result_coords.append((lat, lng))
            store = []
            store.append("https://www.capitalone.com")
            store.append(store_data["locationName"])

            store.append(store_data["address"]["addressLine1"])
            if store[-1].lower() in addresses:
                continue
            addresses.append(store[-1].lower())
            store.append(store_data["address"]["city"])
            store.append(store_data["address"]["state"])
            store.append(store_data["address"]["zipcode"])
            store.append("US")
            store.append(store_data["id"])
            store.append(store_data["phoneNumber"] if "phoneNumber" in store_data and store_data["phoneNumber"] != "" and store_data["phoneNumber"] != None  else "<MISSING>")
            store.append(store_data["locType"])
            store.append(lat)
            store.append(lng)
            hours = ""
            if 'monLobbyHours' in store_data and store_data["monLobbyHours"] != None:
                hours = hours + " monday " + store_data["monLobbyHours"]
            if 'tuesLobbyHours' in store_data and store_data["tuesLobbyHours"] != None:
                hours = hours + " tuesday " + store_data["tuesLobbyHours"]
            if 'wedLobbyHours' in store_data and store_data["wedLobbyHours"] != None:
                hours = hours + " wednesda " + store_data["wedLobbyHours"]
            if 'thurLobbyHours' in store_data and store_data["thurLobbyHours"] != None:
                hours = hours + " thursday " + store_data["thurLobbyHours"]
            if 'friLobbyHours' in store_data and store_data["friLobbyHours"] != None:
                hours = hours + " friday " + store_data["friLobbyHours"]
            if 'satLobbyHours' in store_data and store_data["satLobbyHours"] != None:
                hours = hours + " saturday " + store_data["satLobbyHours"]
            if 'sunLobbyHours' in store_data and store_data["sunLobbyHours"] != None:
                hours = hours + " sunday " + store_data["sunLobbyHours"]
            store.append(hours if hours != "" else "<MISSING>")
            store.append("https://locations.capitalone.com/location/"+str(store_data['id']))
            if "Temporarily Closed" in store_data["locationName"]:
                store.append(store_data["locationName"].split("-")[-1].replace("\xa0"," ").strip())
            else:
                store.append("<MISSING>")
            store = [str(x).encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]
            yield store
            # print("===",store)
        if len(data) < MAX_RESULTS:
            # print("max distance update")
            search.max_distance_update(MAX_DISTANCE)
        elif len(data) == MAX_RESULTS:
            # print("max count update")
            search.max_count_update(result_coords)
        else:
            raise Exception("expected at most " + str(MAX_RESULTS) + " results")
        coord = search.next_coord()


    """  ATMLOC """
    addresses1 = []
    search = sgzip.ClosestNSearch()
    search.initialize()
    MAX_RESULTS = 100
    MAX_DISTANCE = 50.0
    coord = search.next_coord()
    while coord:
        result_coords = []
        # print("remaining zipcodes: " + str(len(search.zipcodes)))
        x = coord[0]
        y = coord[1]
        # print('Pulling Lat-Long %s,%s...' % (str(x), str(y)))
        r_data = '{"lat":' + str(x) + ',"lng":' + str(y) + ',"radius":50,"services":[],"resType":["ATMLOC"]}'
        try:
            r = session.post("https://locations.capitalone.com/resourcelocator/location/resources/",headers=headers,data=r_data)
        except:
            pass
        data = r.json()["resourceList"]
        for store_data in data:
            lat = store_data["latitude"]
            lng = store_data["longitude"]
            result_coords.append((lat, lng))
            store = []
            store.append("https://www.capitalone.com")
            store.append(store_data["locationName"])
            store.append(store_data["address"]["addressLine1"])
            if store[-1].lower() in addresses1:
                continue
            addresses1.append(store[-1].lower())
            store.append(store_data["address"]["city"])
            store.append(store_data["address"]["state"])
            store.append(store_data["address"]["zipcode"])
            store.append("US")
            store.append(store_data["id"])
            store.append(store_data["phoneNumber"] if "phoneNumber" in store_data and store_data["phoneNumber"] != "" and store_data["phoneNumber"] != None  else "<MISSING>")
            store.append(store_data["locType"])
            store.append(lat)
            store.append(lng)
            hours = ""
            if 'monLobbyHours' in store_data and store_data["monLobbyHours"] != None:
                hours = hours + " monday " + store_data["monLobbyHours"]
            if 'tuesLobbyHours' in store_data and store_data["tuesLobbyHours"] != None:
                hours = hours + " tuesday " + store_data["tuesLobbyHours"]
            if 'wedLobbyHours' in store_data and store_data["wedLobbyHours"] != None:
                hours = hours + " wednesda " + store_data["wedLobbyHours"]
            if 'thurLobbyHours' in store_data and store_data["thurLobbyHours"] != None:
                hours = hours + " thursday " + store_data["thurLobbyHours"]
            if 'friLobbyHours' in store_data and store_data["friLobbyHours"] != None:
                hours = hours + " friday " + store_data["friLobbyHours"]
            if 'satLobbyHours' in store_data and store_data["satLobbyHours"] != None:
                hours = hours + " saturday " + store_data["satLobbyHours"]
            if 'sunLobbyHours' in store_data and store_data["sunLobbyHours"] != None:
                hours = hours + " sunday " + store_data["sunLobbyHours"]
            store.append(hours if hours != "" else "<MISSING>")
            store.append("https://locations.capitalone.com/location/"+str(store_data['id']))
            if "Temporarily Closed" in store_data["locationName"]:
                store.append(store_data["locationName"].split("-")[-1].replace("\xa0"," ").strip())
            else:
                store.append("<MISSING>")
            store = [str(x).encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]
            yield store
            # print("===",store)
        if len(data) < MAX_RESULTS:
            # print("max distance update")
            search.max_distance_update(MAX_DISTANCE)
        elif len(data) == MAX_RESULTS:
            # print("max count update")
            search.max_count_update(result_coords)
        else:
            raise Exception("expected at most " + str(MAX_RESULTS) + " results")
        coord = search.next_coord()
    """  ALLPOINTATMLOC """
    addresses2 = []
    search = sgzip.ClosestNSearch()
    search.initialize()
    MAX_RESULTS = 100
    MAX_DISTANCE = 50.0
    coord = search.next_coord()
    while coord:
        result_coords = []
        # print("remaining zipcodes: " + str(len(search.zipcodes)))
        x = coord[0]
        y = coord[1]
        # print('Pulling Lat-Long %s,%s...' % (str(x), str(y)))
        r_data = '{"lat":' + str(x) + ',"lng":' + str(y) + ',"radius":50,"services":[],"resType":["ALLPOINTATMLOC"]}'
        try:
            r = session.post("https://locations.capitalone.com/resourcelocator/location/resources/",headers=headers,data=r_data)
        except:
            pass
        data = r.json()["resourceList"]
        for store_data in data:
            lat = store_data["latitude"]
            lng = store_data["longitude"]
            result_coords.append((lat, lng))
            store = []
            store.append("https://www.capitalone.com")
            store.append(store_data["locationName"])
            store.append(store_data["address"]["addressLine1"])
            if store[-1].lower() in addresses2:
                continue
            addresses2.append(store[-1].lower())
            store.append(store_data["address"]["city"])
            store.append(store_data["address"]["state"])
            store.append(store_data["address"]["zipcode"])
            store.append("US")
            store.append(store_data["id"])
            store.append(store_data["phoneNumber"] if "phoneNumber" in store_data and store_data["phoneNumber"] != "" and store_data["phoneNumber"] != None  else "<MISSING>")
            store.append(store_data["locType"])
            store.append(lat)
            store.append(lng)
            hours = ""
            if 'monLobbyHours' in store_data and store_data["monLobbyHours"] != None:
                hours = hours + " monday " + store_data["monLobbyHours"]
            if 'tuesLobbyHours' in store_data and store_data["tuesLobbyHours"] != None:
                hours = hours + " tuesday " + store_data["tuesLobbyHours"]
            if 'wedLobbyHours' in store_data and store_data["wedLobbyHours"] != None:
                hours = hours + " wednesda " + store_data["wedLobbyHours"]
            if 'thurLobbyHours' in store_data and store_data["thurLobbyHours"] != None:
                hours = hours + " thursday " + store_data["thurLobbyHours"]
            if 'friLobbyHours' in store_data and store_data["friLobbyHours"] != None:
                hours = hours + " friday " + store_data["friLobbyHours"]
            if 'satLobbyHours' in store_data and store_data["satLobbyHours"] != None:
                hours = hours + " saturday " + store_data["satLobbyHours"]
            if 'sunLobbyHours' in store_data and store_data["sunLobbyHours"] != None:
                hours = hours + " sunday " + store_data["sunLobbyHours"]
            store.append(hours if hours != "" else "<MISSING>")
            store.append("https://locations.capitalone.com/location/"+str(store_data['id']))
            if "Temporarily Closed" in store_data["locationName"]:
                store.append(store_data["locationName"].split("-")[-1].replace("\xa0"," ").strip())
            else:
                store.append("<MISSING>")
            store = [str(x).encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]
            yield store

            # print("===",store)
        if len(data) < MAX_RESULTS:
            # print("max distance update")
            search.max_distance_update(MAX_DISTANCE)
        elif len(data) == MAX_RESULTS:
            # print("max count update")
            search.max_count_update(result_coords)
        else:
            raise Exception("expected at most " + str(MAX_RESULTS) + " results")
        coord = search.next_coord()
    
def scrape():
    data = fetch_data()
    write_output(data)

scrape()
