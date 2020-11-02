import csv
import requests
from bs4 import BeautifulSoup
import re
import json
import sgzip

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation",'raw_address'])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36'
    }
    return_main_object = []
    r = requests.get("https://www.vivavitamins.com/store-locator-2/",headers=headers)
    soup = BeautifulSoup(r.text,"lxml")
    for state in soup.find_all("div",{'class':"tab-pane fade fusion-clearfix"}):
        for location in state.find_all("p"):
            location_details = list(location.stripped_strings)
            phone = ""
            number = 0
            for i in range(len(location_details)):
                if "(" in location_details[i] and ")" in location_details[i]:
                    phone = location_details[i]
                    number = i
            for i in range(len(location_details)):
                if "Visit their" in location_details[i]:
                    del location_details[i]
                    break
            store = []
            store.append("https://www.vivavitamins.com")
            store.append(location_details[0])
            del location_details[0]
            store.append("<INACCESSIBLE>")
            store.append("<INACCESSIBLE>")
            store.append("<INACCESSIBLE>")
            store.append("<INACCESSIBLE>")
            store.append("US")
            store.append("<MISSING>")
            store.append(phone.split("|")[0].split("–")[0] if phone != "" else "<MISSING>")
            store.append("<MISSING>")
            store.append("<MISSING>")
            store.append("<MISSING>")
            store.append("<MISSING>")
            if number == 0:
                store.append(" ".join(location_details))
            else:
                store.append(" ".join(location_details[:i-1]))
            return_main_object.append(store)
    for location in soup.find_all("div",{'class':"fusion-button-wrappercenter"})[:-1]:
        location_request = requests.get(location.find("a")["href"],headers=headers)
        location_soup = BeautifulSoup(location_request.text,"lxml")
        if location_soup.find("a",{"href":re.compile("google.com")}) == None:
            continue
        geo_location = location_soup.find("a",{"href":re.compile("google.com")})["href"]
        phone_details = list(location_soup.find("div",{'class':"col-md-3 footer-column"}).stripped_strings)
        address_details = list(location_soup.find("div",{'class':"col-md-3 footer-column"}).stripped_strings)
        if "(" in address_details[1]:
            del address_details[1]
        store = []
        store.append("https://www.vivavitamins.com")
        store.append(location.find("a").text)
        if len(geo_location.split("/")[5].split(",")) != 1:
            store.append(" ".join(address_details[2:-1]))
            store.append(address_details[-1].split(",")[0])
            store.append(address_details[-1].split(",")[1].split(" ")[-2])
            store.append(address_details[-1].split(",")[1].split(" ")[-1])
        else:
            store.append("<INACCESSIBLE>")
            store.append("<INACCESSIBLE>")
            store.append("<INACCESSIBLE>")
            store.append("<INACCESSIBLE>")
        store.append("US")
        store.append("<MISSING>")
        if phone_details[0] == "Contact Us":
            store.append(phone_details[1])
        else:
            store.append("<MISSING>")
        store.append("<MISSING>")
        store.append("<MISSING>")
        store.append(geo_location.split("/@")[1].split(",")[0])
        store.append(geo_location.split("/@")[1].split(",")[1])
        store.append("<INACCESSIBLE>")
        return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
