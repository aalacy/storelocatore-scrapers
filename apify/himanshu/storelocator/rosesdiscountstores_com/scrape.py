import csv
import requests
from bs4 import BeautifulSoup
import re
import json

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    base_url = "https://www.rosesdiscountstores.com"
    return_main_object=[]
    r = requests.get("https://api.zenlocator.com/v1/apps/app_vfde3mfb/locations/search?northeast=82.292271%2C90.127516&southwest=-57.393437%2C-180").json()
    for loc in r['locations']:
        name=loc['name'].strip()
        addr = loc['address'].split(",")
        if "United States" in addr[-1] or "US" in addr[-1]:
            del addr[-1]
        street_address = " ".join(addr[:-2])
        city = addr[-2]
        zipp_list = re.findall(r'\d{5}',addr[-1])
        if zipp_list:
            zipp = zipp_list[-1]
        state = addr[-1].replace(zipp,"").strip()
        
        
        country=loc['countryCode'].strip()
        try:
            phone=loc['contacts']['con_wg5rd22k']['text'].replace("(864) 77702853","(864) 777-2853").strip()
        except:
            phone = "<MISSING>"
        lat=loc['lat']
        lng=loc['lng']
        hour=''
        if 'hours' in loc:
            if 'hoursOfOperation' in loc['hours']:
                for hr in loc['hours']['hoursOfOperation']:
                    hour+=' '+hr+":"+loc['hours']['hoursOfOperation'][hr]
        storeno=''
        store=[]
        store.append(base_url)
        store.append(name if name else "<MISSING>")
        store.append(street_address if street_address else "<MISSING>")
        store.append(city if city else "<MISSING>")
        store.append(state if state else "<MISSING>")
        store.append(zipp if zipp else "<MISSING>")
        store.append(country if country else "<MISSING>")
        store.append(storeno if storeno else "<MISSING>")
        store.append(phone if phone else "<MISSING>")
        store.append("rosesdiscountstores")
        store.append(lat if lat else "<MISSING>")
        store.append(lng if lng else "<MISSING>")
        store.append(hour if hour else "<MISSING>")
        store.append("https://www.rosesdiscountstores.com/store-locator-index")
        store = [str(x).encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]
        yield store

def scrape():
    data = fetch_data()
    write_output(data)
scrape()
