import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json



session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w', encoding="utf-8") as output_file:
        writer = csv.writer(output_file, delimiter=',',
                            quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36'
    }
    base_url = "https://www.lillypulitzer.com"
    rs= "https://www.lillypulitzer.com/on/demandware.store/Sites-lillypulitzer-sfra-Site/default/Stores-FindStores?showMap=true&storeType=ALL_STORES&radius=10000&latitude=39.5243169&longitude=-99.1421644"
    # https://www.lillypulitzer.com/on/demandware.store/Sites-lillypulitzer-us-Site/default/Stores-GetNearestStores?latitude=37.751&longitude=-97.822&countryCode=US&distanceUnit=mi&maxdistance=10000
    r = session.get(rs, headers=headers)
    data = r.json()["stores"]
    return_main_object = []
    for store_data in data:
        store = []
        store_number = store_data['ID']
        new_city  = store_data['city']
        if "Lilly" in store_data['storeType']:
            location_type = store_data['storeType']
        else:
            location_type = "Other Lilly Destinations"

        store.append("https://www.lillypulitzer.com")
        store.append(store_data["name"])
        address2=''
        if store_data["address2"] != None:
            address2 =store_data["address2"]
        store.append(store_data["address1"] + " " + address2)
        store.append(store_data["city"])

        store.append(store_data["stateCode"])
        if len(store_data["stateCode"]) > 2:
            continue
        if store[-1] == "ZZ":
            store[-1] = store_data["city"].split(",")[1]
            store[-2] = store_data["city"].split(",")[0]
        store.append(store_data["postalCode"]
                     if store_data["postalCode"] != "" else "<MISSING>")
        store.append(store_data["countryCode"])
        if len(store_data["postalCode"]) == 7:
            store[-1] = "CA"
        if store[-1] == "":
            store[-1] = "US"
        store.append(store_number)
        store.append(store_data["phone"]
                     if store_data["phone"] != "" else "<MISSING>")
        store.append(location_type)
        store.append(store_data["latitude"])
        store.append(store_data["longitude"])
        hours = ""
        store_hours = store_data["customStoreHours"]
        for key in store_hours:
            hours = hours + " " + key['day'] + " " + key['hours']
        store.append(hours if hours != "" else "<MISSING>")
        page_url = "https://www.lillypulitzer.com/store/details/?storeId="+store_number+"&city="+new_city
        store.append(page_url
                     if page_url != '' else "<MISSING>")
        store = [str(x).encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]
        # print("===" + str(store))
        yield store
        #print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
