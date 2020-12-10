import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
import time
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('samuraisams_net')




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
    r = session.get("https://www.samuraisams.net/locator/index.php?brand=6&mode=desktop&pagesize=10000&latitude=&longitude=&q=11756&submit.x=0&submit.y=0",headers=headers)
    soup = BeautifulSoup(r.text,"lxml")
    for script in soup.find_all("script"):
        if "Locator.stores[" in str(script):
           
            scr = str(script)
            store_data = json.loads('{' + scr.split("{",1)[1].split("}",1)[0] + "}")
            
            if store_data["StatusName"] == "Coming Soon":
                continue
            location_request = session.get("https://www.samuraisams.net/stores/" + str(store_data["StoreId"]),headers=headers)
            location_soup = BeautifulSoup(location_request.text,"lxml")
            name = location_soup.find("h2").text.strip()
            store = []
            store.append("https://www.samuraisams.net")
            store.append(name)
            store.append(store_data["Address"])
            if store[-1][-2] == ",":
                store[-1] = store[-1][:-2]
            if store[-1][-1] == ",":
                store[-1] = store[-1][:-1]
            store.append(store_data["City"])
            store.append(store_data["State"])
            store.append(store_data["Zip"])
            store.append("US")
            store.append(store_data["StoreId"])
            store.append(store_data["Phone"] if store_data["Phone"] else "<MISSING>")
            store.append("<MISSING>")
            store.append(store_data["Latitude"])
            store.append(store_data["Longitude"])
            hours = " ".join(list(location_soup.find("div",{"class":"group hours"}).stripped_strings)).replace('Store Hours ','')
            store.append(hours if hours else "<MISSING>")
            store.append("https://www.samuraisams.net/stores/" + str(store_data["StoreId"]))
            # logger.info(store)
            yield store

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
