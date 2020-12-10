import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
session = SgRequests()
def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        for row in data:
            writer.writerow(row)
def fetch_data():
    adressess = []
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
    }
    base_url = "https://gpminvestments.com/village-pantry"
    r = session.get("https://gpminvestments.com/store-locator/",headers=headers)
    soup = BeautifulSoup(r.text,"lxml")
    json_data = json.loads(str(soup).split('var wpgmaps_localize_marker_data = ')[1].split(';')[0])['7']
    for i in range(2588,2783):
        try:
            location_name = json_data[str(i)]['title']
            if "Pantry" not in location_name:
                continue
            addr = json_data[str(i)]['address'].strip()
            zipp = addr.split(" ")[-1].rstrip("-")
            state = addr.split(" ")[-2]
            city = addr.split(" ")[-3].replace("Graff","De Graff").replace("Point","Russells Point").replace("Center","Jackson Center").replace("Castle","New Castle")
            if "Traverse City" in addr:
                city = "Traverse City"
            elif "Gas City" in addr:
                city = "Gas City"
            elif "Cambridge City" in addr:
                city = "Cambridge City"
            street_address = addr.replace(city,"").replace(state,"").replace(zipp,"").strip()
            latitude = json_data[str(i)]['lat']
            longitude = json_data[str(i)]['lng']
            store_number = json_data[str(i)]['marker_id']
            store = []
            store.append(base_url)
            store.append(location_name)
            store.append(street_address)
            store.append(city)
            store.append(state)
            store.append(zipp)
            store.append("US")
            store.append(store_number)
            store.append("<MISSING>")
            store.append("village Pantry")
            store.append(latitude)
            store.append(longitude)
            store.append("<MISSING>")
            store.append("<MISSING>")
            if store[2] in adressess:
                continue
            adressess.append(store[2])
            store = [str(x).strip() if x else "<MISSING>" for x in store]
            yield store
        except KeyError:
            continue
def scrape():
    data = fetch_data()
    write_output(data)
scrape()
