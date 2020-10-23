
import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
import re
import json
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('domo_ca')


session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w', newline='') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data(): 
    addresses = []
    url = "https://www.domo.ca/locations/"
    response = bs(session.post(url).text,'lxml').text.split("wpgmaps_localize_marker_data =")[1].split("}}};")[0]+"}}}"
    for q in json.loads(response)['1']:
        data = json.loads(response)['1'][q]
        location_name = data['title']
        if data['category']=='1':
            continue

        latitude = data['address'].split(", ")[0]
        longitude = data['address'].split(", ")[1]
        phone = list(bs(data['desc'],'lxml').stripped_strings)[-1]
        city = list(bs(data['desc'],'lxml').stripped_strings)[-2].split(",")[0]
        state = list(bs(data['desc'],'lxml').stripped_strings)[-2].split(",")[1].strip().replace(".",'')
        adr = " ".join(list(bs(data['desc'],'lxml').stripped_strings)[:-1]).replace(location_name,"").replace(city,'').replace(state,"").strip().replace(", .",'').replace(",",'').replace("Can Am Corner Store",'').strip()
        street_address="<MISSING>"
        if adr:
            street_address = (adr)
        zipp ="<MISSING>"
        page_url ="<MISSING>"
        countryCode ="CA"
        hours="<MISSING>"
        store_number = "<MISSING>"
        store = []
        store.append("https://www.domo.ca/")
        store.append(location_name)
        store.append(street_address)
        store.append(city)
        store.append(state)
        store.append(zipp)   
        store.append(countryCode)
        store.append(store_number)
        store.append(phone)
        store.append("<MISSING>")
        store.append(latitude)
        store.append(longitude)
        store.append(hours)
        store.append( "<MISSING>")     
        store = [str(x).encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]
        # if store[2] in addresses:
        #     continue
        # addresses.append(store[2])
       # logger.info("~~~~~~~~~~~~~~~~~~~~~~~~~~~~ ",store)
        yield store

     
    
    
def scrape():
    data = fetch_data()
    write_output(data)

scrape()
