import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re


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
    base_url = "http://fourbrothersstores.com"
    r = session.get(base_url + "/index.cfm/store-locator/")
    soup = BeautifulSoup(r.text,"lxml")
    return_main_object = []
    store_listing = soup.find("div",{"id": "store_listing"})
    store_data = []
    store_names = store_listing.find_all("h3")
    store_details_all = []
    store_details = store_listing.find_all("div",recursive=False)
    for i in range(len(store_details)):
        store_details_all.extend(store_details[i].find_all(("ul"),recursive=False))
    for i in range(len(store_details_all)):
        store_addresses = store_details_all[i].find_all("li",{"class":"txt_address"})
        store_phones = store_details_all[i].find_all("li",{"class":"txt_phone"})
        store_phones_1 = store_details_all[i].find_all("li",{"class":"txt_manager"})
        store_phones.extend(store_phones_1)
        store_hours = store_details_all[i].find_all("li",{"class":"txt_hours"})
        store_diractions = store_details_all[i].find_all("li",{"class":"txt_directions"})
        for j in range(len(store_addresses)):
            store = []
            store_address = list(store_addresses[j].stripped_strings)
            store.append("http://fourbrothersstores.com")
            store.append(store_names[i].text)
            store.append(store_address[0])
            if len(store_address[1].split(",")) == 1:
                store.append(store_address[1].split(" ")[0])
                store.append(store_address[1].split(" ")[1])
                store.append(store_address[1].split(" ")[2])
            else:
                store.append(store_address[1].split(",")[0])
                store.append(store_address[1].split(",")[1].split(" ")[1])
                store.append(store_address[1].split(",")[1].split(" ")[2])
            store.append("US")
            store.append("<MISSING>")
            try:
                store.append(store_phones[j].text.split("Phone:")[1])
            except:
                store.append("<MISSING>")
            store.append("4 brothers")
            try:
                store.append(store_diractions[j].find("a")["href"].split("&sll=")[1].split(",")[0])
                store.append(store_diractions[j].find("a")["href"].split("&sll=")[1].split(",")[1].split("&")[0])
            except:
                store.append("<MISSING>")
                store.append("<MISSING>")
            store.append(store_hours[j].text.split("Hours:")[1])
            return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
