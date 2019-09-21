import csv
import requests
from bs4 import BeautifulSoup
import re
import json
import sgzip
def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    base_url ="https://www.thomassabo.com"
    return_main_object=[]
    output=[]
    cord=sgzip.coords_for_radius(100)
    for cr in cord:
        try:
            r = requests.get(base_url+"/on/demandware.store/Sites-TS_US-Site/en_US/Shopfinder-GetStores?searchMode=radius&searchPhrase=&searchDistance=4934.527951623432&lat="+cr[0]+"&lng="+cr[1]+"&filterBy=").json()
            for loc in r:
                
                if "address1" in loc and "stateCode" in loc:
                    name=loc['name'].strip()
                    address=loc['address1'].strip()
                    city=loc['city'].strip()
                    state=loc['stateCode']
                    zip=''
                    if "postalCode" in loc:
                        zip=loc['postalCode'].strip()
                    if len(zip)==4:
                        zip=str(0)+zip
                    phone=''
                    if "phone" in loc:
                        phone=loc['phone'].strip()
                    country="US"
                    storeno=loc['ID'].strip()
                    lat=loc['latitude']
                    lng=loc['longitude']
                    hour = ''
                    store=[]
                    store.append(base_url)
                    store.append(name if name else "<MISSING>")
                    store.append(address if address else "<MISSING>")
                    store.append(city if city else "<MISSING>")
                    store.append(state if state else "<MISSING>")
                    store.append(zip if zip else "<MISSING>")
                    store.append(country if country else "<MISSING>")
                    store.append(storeno if storeno else "<MISSING>")
                    store.append(phone if phone else "<MISSING>")
                    store.append("thomassabo")
                    store.append(lat if lat else "<MISSING>")
                    store.append(lng if lng else "<MISSING>")
                    store.append(hour if hour.strip() else "<MISSING>")
                    adrr =name+' '+address + ' ' + city + ' ' + state + ' ' + zip
                    if adrr not in output:
                        output.append(adrr)
                        return_main_object.append(store)
        except:
            continue
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)
scrape()
