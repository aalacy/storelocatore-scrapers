import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
# from datetime import datetime

session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        for row in data:
            writer.writerow(row)
def fetch_data():
    addresses = []
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
    }
    base_url = "https://www.schraderoil.com/wp-content/themes/Parallax-One/js/findlocation.js?v=1.05"
    r = session.get(base_url, headers=headers)
    soup = BeautifulSoup(r.text,"lxml")
    m = (soup.text.split("var arStores = [];")[1].split("// new location for stores")[0])
    n = m.split("] = [];")
    # print(n[2])

    for j in range(1,19):
        d = n[j]
        store_number = str(d).split("=")[1].split(";")[0].replace("'","")
        location_name = str(d).split("=")[2].split(";")[0].replace("'","")
        latitude = str(d).split("=")[3].split(";")[0]
        longitude = str(d).split("=")[4].split(";")[0]
        # location_name = str(d).split("=")[5].split(";")[0]
        phone = str(d).split("=")[6].split(";")[0].replace("'","")
        street_address = str(d).split("=")[7].split(";")[0].replace("'","")
        city = str(d).split("=")[8].split(";")[0].replace("'","")
        state = str(d).split("=")[9].split(";")[0].replace("'","")
        zipp = str(d).split("=")[10].split(";")[0].replace("'","")
        store = []
        store.append("https://www.schraderoil.com")
        store.append(location_name if location_name else "<MISSING>")
        store.append(street_address if street_address else "<MISSING>")
        store.append(city if city else "<MISSING>")
        store.append(state if state else "<MISSING>")
        store.append(zipp if zipp else "<MISSING>")
        store.append("US")
        store.append(store_number if store_number else "<MISSING>") 
        store.append(phone if phone else "<MISSING>")
        store.append("Store")
        store.append(latitude if latitude else "<MISSING>")
        store.append(longitude if longitude else "<MISSING>")
        store.append("<MISSING>")
        store.append("https://www.schraderoil.com/find-a-location/")
        # print(store)

        if store[2] in addresses:
            continue
        addresses.append(store[2])
        yield store
def scrape():
    data = fetch_data()
    write_output(data)
scrape()
