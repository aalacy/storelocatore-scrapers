import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
session = SgRequests()
def write_output(data):
    with open('data.csv', mode='w',encoding="utf-8") as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        for row in data:
            writer.writerow(row)
def fetch_data():
    headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36'
    }
    base_url = "http://katieskorner.com"
    r = session.get("http://katieskorner.com/StoreLocations.html",headers=headers)
    soup = BeautifulSoup(r.text,"lxml")
    return_main_object = []
    for location in soup.find_all("blockquote"):
        m_data = list(location.stripped_strings)
        if len(m_data)==4:
            m_data[0:3] = [' '.join(m_data[0:3])]
        for store_data in m_data:
            location_details = store_data.replace("\n"," ").replace("\r","").replace('-',"–").replace('              '," ").replace("–","-").replace("-","-").replace("-","-").replace("•","").replace("Niles - Cortland","Niles-Cortland").strip()
            store = []
            store.append("http://katieskorner.com")
            store.append("Katies Korner - "+ location_details.split(",")[0])
            store.append(location_details.split(" - ")[1].strip())
            store.append(location_details.split(",")[0])
            store.append(location_details.split(" - ")[0].split(",")[1].strip())
            store.append("<MISSING>")
            store.append("US")
            store.append("<MISSING>")
            store.append(location_details.split(" - ")[2] if len(location_details.split(" - ")) == 3 else "<MISSING>")
            store.append("katies korner")
            store.append("<MISSING>")
            store.append("<MISSING>")
            store.append("<MISSING>")
            store.append("<MISSING>")
            return_main_object.append(store)
    return return_main_object
def scrape():
    data = fetch_data()
    write_output(data)
scrape()
