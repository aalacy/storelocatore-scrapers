import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
import re
import json
from datetime import datetime
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
    
    base_url = "https://www.everymancinema.com/"
    soup = bs(session.get("https://www.everymancinema.com/venues-list").content, "lxml")
    
    json_data = json.loads(soup.find(lambda tag: (tag.name == "script") and "pc.venuesList" in tag.text).text.split("pc.venuesList =")[1].replace("current:",'"current":').replace("};","}").replace("\\'","").replace('comingSoon','"comingSoon"'))['current']
    
    for data in json_data:
        
        
        location_name = data['Name']
        street_address = ''
        if data['Cinema']['Address1']:
            street_address += data['Cinema']['Address1']
        if data['Cinema']['Address2']:
            street_address += data['Cinema']['Address2']

        city = data['Cinema']['City']
        state = data['Cinema']['StateName']
        zipp = data['Cinema']['ZipCode']
        country_code = "UK"
        phone = re.findall(r'\d{4}\s+\d{3}\s+\d{4}',data['Cinema']['Phone'])[-1]
        store_number = data['CinemaId']
        location_type = "Cinema"
        lat = data['Cinema']['Latitude']
        lng = data['Cinema']['Longitude']
        hours = data['Cinema']['CinemaInfo']['OpeningTimes']
        
        page_url = base_url + data['UrlFriendlyName']
        
        
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
        store.append(location_type)
        store.append(lat)
        store.append(lng)
        store.append(hours.strip())
        store.append(page_url)     
    
        store = [str(x).encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]
        yield store
        
    
    
def scrape():
    data = fetch_data()
    write_output(data)

scrape()
