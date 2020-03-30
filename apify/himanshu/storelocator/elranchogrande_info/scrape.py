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
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36'
    }
    base_url = "https://elranchogrande.info"
    r = session.get("https://elranchogrande.info/locations/",headers=headers)
    soup = BeautifulSoup(r.text,"lxml")
    return_main_object = []
    for row in soup.find("div",{'class':"post-content"}).find_all("div",recursive=False)[0::2]:
        hours = " ".join(list(row.find_all('div',{'class':"fusion-text"})[-1].stripped_strings))
        for location in row.find('div').find_all("div",{'class':"fusion_builder_column"},recursive=False)[:-1]:
            if location.find("strong") == None:
                continue
            name = location.find("strong").text
            phone = list(location.find("div",{'class':"fusion-text"}).stripped_strings)[-1]
            geo_location = location.find("a",text="View Map")["href"]
            address = geo_location.split("/")[5].replace("+",' ')
            store = []
            store.append("https://elranchogrande.info")
            store.append(name)
            store.append(address.split(",")[0])
            store.append(address.split(",")[1])
            store.append(address.split(",")[-2].split(" ")[-2])
            store.append(address.split(",")[-2].split(" ")[-1])
            store.append("US")
            store.append("<MISSING>")
            store.append(phone)
            store.append("el rancho grande")
            store.append(geo_location.split("/@")[1].split(",")[0])
            store.append(geo_location.split("/@")[1].split(",")[1])
            store.append(hours)
            return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
