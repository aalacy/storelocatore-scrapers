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
    base_url = "https://www.mycornerstonedentist.com/locations/"
    r = session.get(base_url)
    addresses=[]
    soup = BeautifulSoup(r.text,"lxml")
    for q in soup.find_all("div",{"class":"location-detials"}):
        addr = list(q.find("address").stripped_strings)
        name = addr[0]
        address = addr[1]
        city = addr[2].strip().lstrip().replace("\t",'').replace("\n",'').split(",")[0]
        state = addr[2].replace("\t",'').split("\n")[-2]
        zipcodr = addr[2].replace("\t",'').split("\n")[-1]
        phone = addr[3]
        page_url = (q.find("div",text=re.compile("Website")).parent['href'])
        r1 = session.get(page_url)
        soup1 = BeautifulSoup(r1.text,"lxml")
        hours_of_operation = (" ".join(list(soup1.find("table",{"class":"hours-table"}).stripped_strings)))
        latitude = (json.loads(str(soup1).split('"geo":')[1].split('"openingHour')[0].replace("},",'}'))['latitude'])
        longitude = (json.loads(str(soup1).split('"geo":')[1].split('"openingHour')[0].replace("},",'}'))['longitude'])

        store=[]
        store.append(base_url)
        store.append(name)
        store.append(address)
        store.append(city)
        store.append(state)
        store.append(zipcodr)
        store.append("US")
        store.append("<MISSING>")
        store.append(phone)
        store.append("<MISSING>")
        store.append(latitude)
        store.append(longitude)
        store.append(hours_of_operation)
        store.append(page_url)
        if store[2]  in addresses:
                continue
        addresses.append(store[2])
        # print(store)
        yield store
def scrape():
    data = fetch_data()
    write_output(data)
scrape()
