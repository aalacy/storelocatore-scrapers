import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('racetrac_com')




session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w',encoding="utf-8",newline = "") as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36',
    "Content-Type": "application/json; charset=UTF-8"
    }
    addresses=[]
    base_url=locator_domain = "https://racetrac.com"

    r = session.get("https://www.racetrac.com/locations",headers=headers)
    soup = BeautifulSoup(r.text,"lxml")
    data = soup.find(lambda tag: (tag.name == "script") and "var storedata = " in tag.text).text.split("var storedata =")[1].split("];")[0]+"]"
    json_data = json.loads(data)
    for loc in json_data:
        country_code = "US"
        location_type = "<MISSING>"
        store_number = loc["StoreNumber"]
        try:
            location_name = loc["StoreName"]
        except:
            location_name = "<MISSING>"
        if "StoreAddress2" in loc:
            street_address = loc["StoreAddress1"]+" "+loc["StoreAddress2"]
        else:
            street_address = loc["StoreAddress1"]
        try:
            city = loc["StoreCity"]
        except:
            city = "<MISSING>"
        try:
            state = loc["StoreState"]
        except:
            state = "<MISSING>"
        try:
            zipp = loc["StoreZipCode"].strip()
        except:
            zipp = "<MISSING>"
        
        try:
            phone = loc["Phone"]
        except:
            phone = "<MISSING>"
        try:
            latitude = loc["StoreLatitude"]
            longitude = loc["StoreLongitude"]
        except:
            latitude = "<MISSING>"
            longitude = "<MISSING>"
        page_url = "https://www.racetrac.com/Locations/Detail/"+str(store_number)
        
        if loc["Is24Hours"] == True:
            hours_of_operation = "24 Hours / 7 Days"
        else:
            hours_of_operation = "<MISSING>"
        # logger.info(hours_of_operation)
        store = [locator_domain, location_name, street_address, city, state, zipp, country_code,store_number, phone, location_type, latitude, longitude, hours_of_operation, page_url]
        store = ["<MISSING>" if x == "" or x == None else x for x in store]
        # attr = store[2] + " " + store[3]
        if store[-1] in addresses:
            continue
        addresses.append(store[-1])

        # logger.info("data = " + str(store))
        # logger.info('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')

        yield store
   







    # data = '{"swLat":25.82303640133416,"swLng":-115.6947670532553,"neLat":41.79048379771046,"neLng":-61.202579553255305,"features":[]}'
    # r = session.post("https://racetrac.com/Services.asmx/Locate",headers=headers,data=data)
    # logger.info(r.text)
    # exit()
    # return_main_object = []
    # location_list = r.json()
    # store_ids = []
    # for key in location_list:
    #     if "Stores" in location_list[key]:
    #         for store_data in location_list[key]["Stores"]:
    #             store = []
    #             store.append("https://racetrac.com")
    #             store.append("<MISSING>")
    #             store.append(store_data["Address"])
    #             store.append(store_data['City'])
    #             store.append(store_data['State'])
    #             store.append(store_data["ZipCode"])
    #             store.append("US")
    #             store.append(store_data["StoreNumber"])
    #             if store[-1] in store_ids:
    #                 continue
    #             store_ids.append(store[-1])
    #             store.append(store_data["PhoneNumber"].split("x")[0] if store_data["PhoneNumber"] else "<MISSING>")
    #             store.append("<MISSING>")
    #             store.append(store_data["Latitude"] if store_data["Latitude"] != 0 else "<MISSING>")
    #             store.append(store_data["Longitude"] if store_data["Longitude"] != 0 else "<MISSING>")
    #             store.append("<MISSING>")
    #             store.append("<MISSING>")
    #             yield store
    #             logger.info(store)

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
