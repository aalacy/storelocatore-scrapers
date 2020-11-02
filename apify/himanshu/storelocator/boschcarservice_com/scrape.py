import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json


session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    base_url = "https://am.boschcarservice.com"
    return_main_object = []
    r = session.get("https://ws12-mtp.boschwebservices.com/RB.GEOLOCATOR/GeoLocator.svc/SearchLocations/ByLocator/US/41?format=json&numResults=100000")
    data = r.json()["Locations"]
    for i in range(len(data)):
        store_data = data[i]
        store = []
        store.append("https://am.boschcarservice.com")
        store.append(store_data["LocationName"])
        store.append(store_data["Address"]["Address2"]  + " " + store_data["Address"]["Address1"] if "Address2" in  store_data["Address"] and store_data["Address"]["Address2"] != None else store_data["Address"]["Address1"])
        store.append(store_data["Address"]["City"])
        store.append(store_data["Address"]["State"])
        store.append(store_data["Address"]["PostalCode"])
        store.append(store_data["Address"]["Country"])
        store.append(store_data["LocationID"])
        if store_data["Resources"][1]["Name"] == "Telephone":
            store.append(store_data["Resources"][1]["Value"])
        else:
            store.append("<MISSING>")
        store.append(store_data["BrandDescription"])
        store.append(store_data["Geo"]["Latitude"])
        store.append(store_data["Geo"]["Longitude"])
        hours = ""
        store_hours = store_data["Hours"].split(";")
        hours_object = {"0": "Monday","1":"Tuesday","2":"Wednesday","3":"Thursday","4":"Friday","5":"Saturday","6":"Sunday"}
        for j in range(len(store_hours)):
            if store_hours[j].split(",")[0] == "" or store_hours[j].split(",")[0] == " ":
                pass
            else:
                hours = hours + hours_object[store_hours[j].split(",")[0]] + " " + store_hours[j].split(",")[-2] + " to " + store_hours[j].split(",")[-1] + " "
        store.append(hours if hours != "" else "<MISSING>")
        return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
