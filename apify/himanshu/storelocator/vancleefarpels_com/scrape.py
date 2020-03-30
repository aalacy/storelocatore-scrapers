import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json


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
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36',
        'Host': "www.vancleefarpels.com",
        "Referer": "https://www.vancleefarpels.com/us/en/store-locator.html",
        "X-Requested-With": "XMLHttpRequest",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8" # application/x-www-form-urlencoded; charset=UTF-8"
    }
    base_url = "https://www.vancleefarpels.com"
    data = "actionName=StoreSearchAction&currentPagePath=%2Fcontent%2Fvca%2Fus%2Fusa%2Fen%2Fhome%2Fstore-locator&dataType=default"
    r = session.post("https://www.vancleefarpels.com/cms-base/richemont/form/actionController",headers=headers,data=data)
    data = r.json()["content"]
    return_main_object = []
    for store_data in data:
        if store_data["country"] != "USA" and store_data["country"] != "Canada":
            continue
        location_request = session.get(base_url + store_data["url"])
        location_soup = BeautifulSoup(location_request.text,"lxml")
        hours = " ".join(list(location_soup.find("strong",text="Opening Hours").parent.stripped_strings)).replace("\n"," ").replace("\r"," ").replace("\t"," ").replace("  ","")
        store = []
        store.append("https://www.vancleefarpels.com")
        store.append(store_data["name"])
        store.append(" ".join(list(BeautifulSoup(store_data["street"],"lxml").stripped_strings)))
        store.append(store_data["city"] if store_data["city"] != "" else "<MISSING>")
        store.append(store_data["state"] if store_data["state"] != "" else "<MISSING>")
        store.append(store_data["zipcode"] if store_data["zipcode"] != "" else "<MISSING>")
        store.append("US" if store_data["country"] == "USA" else "CA")
        if store[-1] == "CA":
            if len(store[-2]) > 8:
                store[-3] = store[-2].split(" ")[0]
                store[-2] = " ".join(store[-2].split(" ")[1:])
        store.append(store_data["sid"])
        store.append(store_data["phone"])
        store.append("van cleef & arples")
        store.append(store_data["latitude"])
        store.append(store_data["longitude"])
        store.append(hours)
        store.append(base_url + store_data["url"])
        yield store

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
