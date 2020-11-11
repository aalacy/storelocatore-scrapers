import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
from sglogging import SgLogSetup
logger = SgLogSetup().get_logger('backyardburgers_com')
session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)
def fetch_data():
    addressess = []
    base_url= "https://www.backyardburgers.com/store-locator/"
    r = session.get(base_url)
    soup= BeautifulSoup(r.text,"lxml")
    jd = json.loads(str(soup).split("locations: ")[1].split('apiKey: ')[0].strip().rstrip(","))
    for val in jd:
        location_name = val['name']
        street_address = val['street']
        city = val['city']
        state = val['state']
        zipp = val['postal_code']
        store_number = val['id']
        phone = val['phone_number']
        latitude = val['lat']
        longitude = val['lng']
        page_url = "https://www.backyardburgers.com"+val['url']
        h_data = BeautifulSoup(val['hours'],'html5lib')
        if page_url=="https://www.backyardburgers.com/location/back-yard-burgers-batesville/":
            hours_of_operation = "temporarily closed"
        else:
            hoo = list(h_data.find("p").stripped_strings)
            hour = []
            for h in hoo:
                hour.append(" ".join(h.split()))
            hours_of_operation = ", ".join(hour).replace(", *Dinning room closes at 7:00 pm","").replace("Now Open!","<MISSING>").replace("Closed for renovations","")
            
        
        store = []
        store.append("https://www.backyardburgers.com")
        store.append(location_name if location_name else '<MISSING>')
        store.append(street_address if street_address else '<MISSING>')
        store.append(city if city else '<MISSING>')
        store.append(state if state else '<MISSING>')
        store.append(zipp if zipp else '<MISSING>')
        store.append("US")
        store.append(store_number)
        store.append(phone if phone else '<MISSING>')
        store.append("Back Yard Burgers")
        store.append(latitude if latitude else '<MISSING>')
        store.append(longitude if longitude else '<MISSING>')
        store.append(hours_of_operation.replace("Nov 11th (Remembrance Day) ",'') if hours_of_operation else '<MISSING>')
        store.append(page_url)
        store = [x.encode('ascii', 'ignore').decode('ascii').strip() if type(x) == str else x for x in store]
        if store[2] in addressess:
            continue
        addressess.append(store[2])
        yield store
        
def scrape():
    data = fetch_data()
    write_output(data)
scrape()


