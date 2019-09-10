import csv
import requests
from bs4 import BeautifulSoup
import re
import json

def write_output(data):
    with open('data.csv', mode='w',encoding="utf-8") as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36'
    }
    base_url = "https://www.tedbaker.com"
    r = requests.get("https://www.tedbaker.com/us/json/stores/for-country?isocode=US",headers=headers)
    data = r.json()["data"]
    return_main_object = []
    for i in range(len(data)):
        store_data = data[i]
        store = []
        store.append("https://www.tedbaker.com")
        store.append(store_data["displayName"])
        if "line1" in store_data["address"]:
            store.append(store_data["address"]["line1"] + " " + store_data["address"]["line2"] if "line2" in store_data["address"] else store_data["address"]["line1"])
        else:
            if "line2" in store_data["address"]:
                store.append(store_data["address"]["line2"])
            else:
                continue
        if "line3" in store_data["address"]:
            store.append(store_data["address"]["line3"])
        else:
            if "town" in store_data["address"]:
                store.append(store_data["address"]["town"])
            else:
                store.append("<MISSING>")
        if "postalCode" in store_data["address"]:
            if "region" in store_data["address"]:
                if store_data["address"]["postalCode"] == "-":
                    store.append(store_data["address"]["region"]["isocodeShort"])
                    store.append(store_data["address"]["town"].split(" ")[-1])
                else:
                    store.append(store_data["address"]["region"]["isocodeShort"])
                    store.append(store_data["address"]["postalCode"].split(" ")[-1])
            else:
                if len(store_data["address"]["postalCode"].split(" ")) == 2:
                    store.append(store_data["address"]["postalCode"].split(" ")[0])
                    store.append(store_data["address"]["postalCode"].split(" ")[-1])
                else:
                    store.append("<MISSING>")
                    store.append(store_data["address"]["postalCode"])
        else:
            if "region" in store_data["address"]:
                store.append(store_data["address"]["region"]["isocodeShort"])
                store.append("<MISSING>")
            else:
                if "town" in store_data["address"]:
                    if "line3" in store_data["address"] and len(store_data["address"]["line3"].split(",")) == 2:
                        store.append(store_data["address"]["line3"].split(",")[1].split(" ")[-2])
                        store.append(store_data["address"]["line3"].split(" ")[-1])
                    else:
                        store.append(store_data["address"]["town"].split(" ")[0])
                        store.append(store_data["address"]["town"].split(" ")[-1])
                else:
                    store.append(store_data["address"]["line3"].split(" ")[0])
                    store.append(store_data["address"]["line3"].split(" ")[-1])
        if len(store[-3]) == 2 and store[-3].isupper():
            store[-3] = store_data["address"]["line2"]
            store[-2] = store_data["address"]["line3"]
        if store[-2] == "<MISSING>":
            if len(store_data["address"]["town"]) == 2 and store_data["address"]["town"].isupper():
                store[-2] = store_data["address"]["town"]
        if "City" in store[2]:
            if "City" in store_data["address"]["line1"]:
                store[2] = store_data["address"]["line3"] + " " + store_data["address"]["line2"]
                store[3] = store_data["address"]["line1"]
        if "Space" in store[3]:
            store[3] = store_data["address"]["town"]
        if 'Miami Beach' in store[2]:
            store[2] = store[2].replace("Miami Beach","")
            store[3] = "Miami Beach"
        if store[-1] == "":
            store[-1] = store_data["address"]["postalCode"].split(" ")[1]
        if store[-3] == "Nevada":
            store[-3] = store_data["address"]["town"]
        if store[-3].split(" ")[0].isdigit():
            store[-3] = store_data["address"]["town"]
        if "New York City" in store[2]:
            store[2] = store[2].replace("New York City","")
            store[3] = "New York City"
        if store[-1] in store[-3]:
            store[-3] = store[-3].split(",")[0]
        if store[1].replace("- ","") in store[2]:
            store[2] = store[2].replace(store[1].replace("- ",""),"")
        store.append(store_data["address"]["country"]["isocode"])
        store.append(store_data["openingHours"]["code"])
        store.append(store_data["address"]["phone"] if "phone" in store_data["address"] and store_data["address"]["phone"] != "" and store_data["address"]["phone"] != None else "<MISSING>")
        store.append("ted baker")
        store.append(store_data["geoPoint"]["latitude"])
        store.append(store_data["geoPoint"]["longitude"])
        hours = ""
        store_hours = store_data["openingHours"]["weekDayOpeningList"]
        for k in range(len(store_hours)):
            if store_hours[k]["closed"] == True:
                hours = hours + " closed " + store_hours[k]["weekDay"]
            else:
                hours = hours + " " + store_hours[k]["weekDay"] + " open time " + store_hours[k]["openingTime"]["formattedHour"] + " close time " + store_hours[k]["closingTime"]["formattedHour"]
        store.append(hours if hours != "" else "<MISSING>")
        for i in range(len(store)):
            if type(store[i]) == str:
                store[i] = store[i].replace("–","-")
        return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
