import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
import sgzip


session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36'
    }
    r = session.get("https://www.sherwin-williams.com/store-locator",headers=headers)
    soup = BeautifulSoup(r.text,"lxml")
    location_types = []
    for option in soup.find("select",{"id":"findstores_selectStoreType"}).find_all("option"):
        location_types.append(option["value"])
    store_id = soup.find("meta",{'name':"CommerceSearch"})["content"].split("_")[-1]
    for script in soup.find_all("script"):
        if 'WCParamJS ' in script.text:
            catalogId = script.text.split("catalogId")[1].split(",")[0].replace("'","").replace('"',"").replace(":","")
    return_main_object = []
    addresses = []
    MAX_RESULTS = 25
    MAX_DISTANCE = 75.0
    r_headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
        "X-Requested-With": "XMLHttpRequest",
        "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
        "Accept": "application/json, text/plain, */*"
    }
    for loc_type in location_types:
        search = sgzip.ClosestNSearch()
        search.initialize()
        coord = search.next_coord()
        while coord:
            result_coords = []
            # print("remaining zipcodes: " + str(search.zipcodes_remaining()))
            x = coord[0]
            y = coord[1]
            # print('Pulling Lat-Long %s,%s...' % (str(x), str(y)))
            r_data = 'sideBarType=LSTORES&latitude=' + str(x) + '&longitude=' + str(y) + '&radius=75&uom=SMI&abbrv=us&storeType=' + loc_type + '&countryCode=&requesttype=ajax&langId=&storeId=' + str(store_id)  + '&catalogId=' + str(catalogId)
            r = session.post("https://www.sherwin-williams.com/AjaxStoreLocatorSideBarView?langId=-1&storeId=" + str(store_id),headers=r_headers,data=r_data)
            soup = BeautifulSoup(r.text,"lxml")
            data = json.loads(soup.find("script",{'id':"storeResultsJSON"}).text)["stores"]
            for store_data in data:
                lat = store_data["latitude"]
                lng = store_data["longitude"]
                result_coords.append((lat, lng))
                store = []
                store.append("https://www.sherwin-williams.com")
                store.append(store_data["name"])
                store.append(store_data["address"])
                if store[-1] in addresses:
                    continue
                addresses.append(store[-1])
                store.append(store_data["city"])
                store.append(store_data["state"])
                store_data["zipcode"] = store_data["zipcode"].replace("                                   ","")
                if store_data["zipcode"].replace(" ","").replace("-","").isdigit():
                    store.append(store_data["zipcode"].replace(" ",""))
                    store.append("US")
                else:
                    ca_zip = store_data["zipcode"].replace(" ","")
                    store.append(ca_zip[:3] + " " + ca_zip[3:])
                    store.append("CA")
                store.append(store_data["url"].split("storeNumber=")[1])
                store.append(store_data["phone"].replace("  ","") if "phone" in store_data and store_data["phone"] != "" and store_data["phone"] != None  else "<MISSING>")
                store.append(loc_type)
                store.append(lat)
                store.append(lng)
                location_request = session.get("https://www.sherwin-williams.com" + store_data["url"],headers=headers)
                location_soup = BeautifulSoup(location_request.text,"lxml")
                hours = " ".join(list(location_soup.find("div",{'class':"store-hours-table"}).stripped_strings))
                store.append(hours if hours != "" else "<MISSING>")
                store.append("<MISSING>")
                # print(store)
                yield store
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