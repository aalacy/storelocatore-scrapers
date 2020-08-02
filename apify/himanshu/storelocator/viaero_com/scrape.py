import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
session = SgRequests()
def write_output(data):
    with open('data.csv', mode='w',encoding="utf-8") as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    base_url = "https://www.viaero.com"
    state_list = ["AL","AK","AZ","AR","CA","CO","CT","DE","FL","GA","HI","ID","IL","IN","IA","KS","KY","LA","ME","MD","MA","MI","MN","MS","MO","MT","NE","NV","NH","NJ","NM","NY","NC","ND","OH",'OK',"OR","PA","RI","SC","SD",'TN',"TX","UT","VT","VA","WA","WV","WI","WY"]
    
    addressess = []
    for region in state_list:
        json_data = session.get("https://stores.viaero.com/modules/multilocation/?near_location="+str(region)+"&services__in=&within_business=true").json()['objects']

        for data in json_data:

            location_name = data['location_name']
            street_address = data['street']
            city = data['city']
            state = data['state']
            zipp = data['postal_code']
            country_code = data['country']
            store_number = data['id']
            phone = data['phonemap']['phone']
            lat = round(float(data['lat']),6)
            lng = round(float(data['lon']),6)
            hours = ""
            for label in data['formatted_hours']['primary']['days']:
                hours+= " "+label['label']+" "+label['content']+" "
           
    
            page_url = data['location_url']

            store = []
            store.append(base_url)
            store.append(location_name)
            store.append(street_address)
            store.append(city)
            store.append(state)
            store.append(zipp)
            store.append(country_code)
            store.append(store_number)
            store.append(phone)
            store.append("<MISSING>")
            store.append(lat)
            store.append(lng)
            store.append(hours.strip())
            store.append(page_url)

            if store[2] in addressess:
                continue
            addressess.append(store[2])  
            store = [str(x).encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]          
            yield store

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
