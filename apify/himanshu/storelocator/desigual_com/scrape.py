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
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36'
    }
    return_main_object = []
    addresses = []
    coords = sgzip.coords_for_radius(200)
    for coord in coords:
        #print("https://www.desigual.com/on/demandware.store/Sites-dsglcom_prod_at-Site/de_AT/Stores-FindStores?showMap=true&radius=200&showOnlyAllowDevosStores=false&showOfficialStores=false&showOutlets=false&showAuthorized=false&lat="+ str(coord[0]) + "&long=" + str(coord[1]))
        r = session.get("https://www.desigual.com/on/demandware.store/Sites-dsglcom_prod_at-Site/de_AT/Stores-FindStores?showMap=true&radius=200&showOnlyAllowDevosStores=false&showOfficialStores=false&showOutlets=false&showAuthorized=false&lat="+ str(coord[0]) + "&long=" + str(coord[1]),headers=headers)
        data = r.json()["stores"]
        for store_data in data:
            if store_data["countryCode"] not in ["US","CA"]:
                continue
            store = []
            store.append("https://www.desigual.com")
            store.append(store_data["name"])
            store.append(store_data["address1"] + " " + store_data["address2"] if store_data["address2"] else store_data["address1"])
            if store[-1] in addresses:
                continue
            addresses.append(store[-1])
            if store_data["city"]:
                store.append(store_data["city"] if store_data["city"] else "<MISSING>")
            elif "cityExternalName" in store_data:
                store.append(store_data["cityExternalName"] if store_data["cityExternalName"] else "<MISSING>")
            else:
                store.append("<MISSING>")
            store.append(store_data["locationSapCode"]  if "locationSapCode" in store_data else "<MISSING>")
            store.append(store_data["postalCode"] if store_data["postalCode"] else "<MISSING>")
            if store[-1] == "<MISSING>":
                store.append(store_data["countryCode"])
            else:
                store.append(store_data["countryCode"] if store_data["postalCode"].replace("-","").replace(" ","").isdigit() else "CA")
            if store[-1] == "CA":
                store[-2] = store[-2].upper()
            store.append("<MISSING>")
            store.append(store_data["phone"] if "phone" in store_data and store_data["phone"] and store_data["phone"] != "Not Available" else "<MISSING>")
            store.append("<MISSING>")
            store.append(store_data["latitude"])
            store.append(store_data["longitude"])
            hours = ""
            days = {1:"Sunday",2:"Monday",3:"Tuesday",4:"Wednesday",5:"Thursday",6:"Friday",7:"Saturday"}
            if "schedule" in store_data and store_data["schedule"]:
                store_hours = store_data["schedule"]
                for hour in store_hours:
                    hours = hours + " " + days[hour["dayNumber"]] + " " + hour["value"]
            store.append(hours if hours != "" else "<MISSING>")
            store.append("<MISSING>")
            #print(store)
            yield store

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
