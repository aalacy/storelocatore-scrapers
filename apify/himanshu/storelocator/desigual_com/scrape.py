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
    base_url = "https://www.desigual.com"
    r = requests.get("https://www.desigual.com/en_US/stores/world/",headers=headers)
    soup = BeautifulSoup(r.text,"lxml")
    return_main_object = []
    for country in soup.find("div",{'class':"world-list"}).find_all("a"):
        if country.text == "USA":
            current_country = "US"
        elif country.text == "Canada":
            current_country = "CA"
        else:
            continue
        country_request = requests.get(base_url + country["href"],headers=headers)
        country_soup = BeautifulSoup(country_request.text,"lxml")
        for location in country_soup.find_all("li",{"class":"grid-mobile-cols-10 grid-tablet-cols-333"}):
            location_request = requests.get(base_url + location.find("a")["href"],headers=headers)
            location_soup = BeautifulSoup(location_request.text,"lxml")
            for script in location_soup.find_all("script"):
                if "window.dgl.storeLocatorDetail = " in script.text:
                    store_data = json.loads(script.text.split("window.dgl.storeLocatorDetail = ")[-1].split("};")[0] + "}")
            store = []
            store.append("https://www.desigual.com")
            store.append(store_data["name"])
            store.append(store_data["displayAddress"])
            store.append(store_data["cityName"])
            store.append("<MISSING>")
            store.append(store_data["postalCode"])
            store.append(current_country)
            store.append(store_data["id"])
            store.append(store_data["phoneNumber"] if "phoneNumber" in store_data else "<MISSING>")
            store.append("desigual")
            store.append(store_data["coordinates"]["latitude"] if store_data["coordinates"] != {} else "<MISSING>")
            store.append(store_data["coordinates"]["longitude"] if store_data["coordinates"] != {} else "<MISSING>")
            hours = ""
            hours = hours + " Mon - Sat: " + store_data["workingHoursOpen"] + " - " + store_data["workingHoursClose"]
            if store_data["openOnSunday"] == True:
                hours = hours + " Open on Sundays: Yes "
            else:
                hours = hours + " Open on Sundays: No "
            store.append(hours)
            return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
