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
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    zips = sgzip.for_radius(100)
    return_main_object = []
    addresses = []
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36'
    }
    app_key_request = session.get("https://hosted.where2getit.com/northface/2015/index.html")
    app_key_soup = BeautifulSoup(app_key_request.text,"lxml")
    for script in app_key_soup.find_all("script"):
        if "appkey: " in script.text:
            app_key = script.text.split("appkey: ")[1].split(",")[0].replace("'","")
    for zip_code in zips[3:]:
       
        base_url = "https://www.thenorthface.com"
        data = '{"request":{"appkey":"' + app_key + '","formdata":{"geoip":false,"dataview":"store_default","limit":1000,"order":"rank, _DISTANCE","geolocs":{"geoloc":[{"addressline":"' + str(zip_code) + '","country":"US","latitude":"","longitude":""}]},"searchradius":"100","where":{"visiblelocations":{"eq":""},"or":{"northface":{"eq":""},"outletstore":{"eq":""},"retailstore":{"eq":""},"summit":{"eq":""}},"and":{"youth":{"eq":""},"apparel":{"eq":""},"footwear":{"eq":""},"equipment":{"eq":""},"mt":{"eq":""},"access_pack":{"eq":""},"steep_series":{"eq":""}}},"false":"0"}}}'
        r = session.post("https://hosted.where2getit.com/northface/2015/rest/locatorsearch?lang=en_EN",headers=headers,data=data)
        if "collectioncount" not in r.json()["response"]:
            continue
        for store_data in r.json()["response"]["collection"]:
            store = []
            store.append("https://www.thenorthface.com")
            store.append(store_data["name"])
            address = ""
            if store_data["address1"] != None:
                address = address + store_data["address1"]
            if store_data["address2"] != None:
                address = address + store_data["address2"]
            if address == "":
                continue
            store.append(address)
            if store[-1] in addresses:
                continue
            addresses.append(store[-1])
            store.append(store_data["city"])
            store.append(store_data["state"] if store_data["country"] == "US" else store_data["province"])
            if store[-1] == None:
                store[-1] = "<MISSING>"
            store.append(store_data["postalcode"] if store_data["postalcode"] != "" and store_data["postalcode"] != None else "<MISSING>")
            store.append(store_data["country"])
            store.append(store_data["storenumber"] if store_data["storenumber"] != None else "<MISSING>")
            store.append(store_data["phone"].split("or")[0].split(";")[0].split("and")[0] if store_data["phone"] != None and store_data["phone"] != "TBD" else "<MISSING>")
            store.append("the north face")
            store.append(store_data["latitude"])
            store.append(store_data["longitude"])
            hours = ""
            if store_data["m"] != None:
                hours = hours + " Monday " + store_data["m"]
            if store_data["t"] != None:
                hours = hours + " Tuesday " + store_data["t"]
            if store_data["w"] != None:
                hours = hours + " Wednesday " + store_data["w"]
            if store_data["thu"] != None:
                hours = hours + " Thursday " + store_data["thu"]
            if store_data["f"] != None:
                hours = hours + " Friday " + store_data["f"]
            if store_data["sa"] != None:
                hours = hours + " Saturday " + store_data["sa"]
            if store_data["su"] != None:
                hours = hours + " Sunday " + store_data["su"]
            store.append(hours if hours != "" else "<MISSING>")
          
            return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
