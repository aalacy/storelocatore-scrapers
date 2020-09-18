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
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
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
        for location in row.find('div').find_all("div",{'class':"fusion_builder_column"},recursive=False)[:-1]:
            if location.find("strong") == None:
                continue
            name = location.find("strong").text
            if "coming" in name.lower():
                continue
            phone = list(location.find("div",{'class':"fusion-text"}).stripped_strings)[-1]
            geo_location = location.find_all("a")[-1]["href"]
            address = geo_location.split("/")[5].replace("+",' ')
            street_address = address.split(",")[0].replace("-",' ')
            try:
                float(street_address)
                raw_address = location.p.text.replace("\n"," ")
                raw_address = raw_address[:raw_address.find("Phone")].replace(",","").strip().split()
                street_address = " ".join(raw_address[:-3])
                city = raw_address[-3]
                state = raw_address[-2]
                zip_code = raw_address[-1]
            except:
                city = address.split(",")[1]
                state = address.split(",")[-2].split(" ")[-2]
                zip_code = address.split(",")[-2].split(" ")[-1]
            store = []
            store.append("https://elranchogrande.info")
            store.append("https://elranchogrande.info/locations/")
            store.append(name)
            store.append(street_address)
            store.append(city.strip())
            store.append(state)
            store.append(zip_code)
            store.append("US")
            store.append("<MISSING>")
            store.append(phone)
            store.append("<MISSING>")
            store.append(geo_location.split("/@")[1].split(",")[0])
            store.append(geo_location.split("/@")[1].split(",")[1])
            store.append("<MISSING>")
            return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
