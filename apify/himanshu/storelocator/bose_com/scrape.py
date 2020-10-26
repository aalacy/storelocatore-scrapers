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
    base_url = "https://www.bose.com"
    return_main_object = []
    r = session.get("https://bose.brickworksoftware.com/locations_search?hitsPerPage=10&page=0&getRankingInfo=true&facets[]=*&aroundRadius=all&filters=domain:bose.brickworksoftware.com+AND+publishedAt%3C%3D1563099396528&esSearch={%22page%22:" + str(0)+ ",%22storesPerPage%22:50,%22domain%22:%22bose.brickworksoftware.com%22,%22locale%22:%22en_US%22,%22must%22:[{%22type%22:%22range%22,%22field%22:%22published_at%22,%22value%22:{%22lte%22:1563099396528}}],%22filters%22:[],%22aroundLatLngViaIP%22:true}&aroundLatLngViaIP=true")
    data = r.json()
    page_id = data["nbPages"]
    for k in range(0,page_id):
        print(k)
        r = session.get("https://bose.brickworksoftware.com/locations_search?hitsPerPage=10&page=0&getRankingInfo=true&facets[]=*&aroundRadius=all&filters=domain:bose.brickworksoftware.com+AND+publishedAt%3C%3D1563099396528&esSearch={%22page%22:" + str(k)+ ",%22storesPerPage%22:50,%22domain%22:%22bose.brickworksoftware.com%22,%22locale%22:%22en_US%22,%22must%22:[{%22type%22:%22range%22,%22field%22:%22published_at%22,%22value%22:{%22lte%22:1563099396528}}],%22filters%22:[],%22aroundLatLngViaIP%22:true}&aroundLatLngViaIP=true")
        data = r.json()["hits"]
        for i in range(len(data)):
            store_data = data[i]
            store = []
            store.append("https://www.bose.com")
            store.append(store_data["attributes"]["name"])
            store.append(store_data["attributes"]["address1"] + store_data["attributes"]["address2"] if store_data["attributes"]["address2"] != None else store_data["attributes"]["address1"])
            store.append(store_data["attributes"]["city"])
            store.append(store_data["attributes"]["state"])
            store.append(store_data["attributes"]["postalCode"])
            store.append(store_data["attributes"]["countryCode"])
            store.append(store_data["id"])
            if 'This location is closed' in store_data["attributes"]["phoneNumber"]:
                continue
            store.append(store_data["attributes"]["phoneNumber"])
            store.append("bose")
            store.append(store_data["_geoloc"]["lat"])
            store.append(store_data["_geoloc"]["lng"])
            hours = ""
            store_hours = store_data["relationships"]["hours"]
            for j in range(len(store_hours)):
                if store_hours[j]["closed"] == True or store_hours[j]["closed"] == "true":
                    pass
                else:
                    hours = hours + store_hours[j]["displayDay"] + " " + store_hours[j]["startTime"] + " " + store_hours[j]["endTime"] + " "
            store.append(hours if hours != "" else "<MISSING>")
            return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
