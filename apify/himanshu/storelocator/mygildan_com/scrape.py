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
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    headers = {
        "user-agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36"
    }
    base_url = "https://www.mygildan.com"
    r = session.get("https://www.mygildan.com/store/us/inventory/distributorMap.jsp",headers=headers)
    soup = BeautifulSoup(r.text,"lxml")
    return_main_object = []
    for script in soup.find_all("script"):
        if "var distributorData = " in script.text:
            location_text = script.text.split("var distributorData = ")[1].split("];")[0] + "]"
            location_list = json.loads(re.sub("(\w+):", r'"\1":',location_text.replace("\t","").replace("    ","").replace("shipToId",'"shipToId"')))
            for store_data in location_list:
                store = []
                store.append("https://www.mygildan.com")
                store.append(store_data["name"])
                store.append(" ".join(store_data["contact"]["address"].split(",")[:-4]))
                store.append(store_data["contact"]["address"].split(",")[-4])
                store.append(store_data["contact"]["address"].split(",")[-3] if store_data["contact"]["address"].split(",")[-3] != " " else "<MISSING>")
                store.append(store_data["contact"]["address"].split(",")[-2])
                store.append("US")
                store.append("<MISSING>")
                store.append(store_data["contact"]["phone"])
                store.append("gildan")
                store.append(store_data["lat"])
                store.append(store_data["lng"])
                store.append("<MISSING>")
                store.append("<MISSING>")
                yield store

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
