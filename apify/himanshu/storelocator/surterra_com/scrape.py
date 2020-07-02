import csv
from bs4 import BeautifulSoup as bs
import re
import json
from datetime import datetime
from sgrequests import SgRequests
import platform
from sgselenium import SgSelenium

def write_output(data):
    with open('data.csv', mode='w', newline='') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)

session = SgRequests()
driver = SgSelenium().chrome()

def get_hours(page_url):
    driver.get(page_url)
    location_soup = bs(driver.page_source,"lxml")
    ld_json = location_soup.find('script',type="application/ld+json").string
    lines = ld_json.splitlines()
    for i in range(len(lines)):
        if 'openingHours' in lines[i]:
            hours = ', '.join(x.strip('",[] ') for x in lines[i+1].split(',')).strip('",[] ')
            return hours

def fetch_data(): 
    base_url = "https://www.surterra.com/"

    soup = bs(session.get("https://www.surterra.com/stores/").text, "lxml")

    json_data = json.loads(soup.find(lambda tag: (tag.name == "script") and '"zip"' in tag.text).text.split("window.storesLocationData =")[-1])['Florida']
    for key,value in json_data.items():
        
        location_name = value['title']

        street_address = value['street']
        city = value['city']
        state = value['state']
        zipp = value['zip']
        phone = value['formatted_phone']
        lat = value['geo']['lat']
        lng = value['geo']['lng']
        store_number = value['pickup_location_id']

        page_url = "https://www.surterra.com/stores/"+str(value['slug'])
        hours = '<MISSING>'
        try:
            hours = get_hours(page_url) 
        except:
            print("failed to retrieve hours for {}".format(page_url))

        store = []
        store.append(base_url)
        store.append(location_name)
        store.append(street_address)
        store.append(city)
        store.append(state)
        store.append(zipp)   
        store.append("US")
        store.append(store_number)
        store.append(phone)
        store.append("<MISSING>")
        store.append(lat)
        store.append(lng)
        store.append(hours.replace('Hours ',''))
        store.append(page_url)     
        store = [str(x).encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]
        yield store
    
def scrape():
    data = fetch_data()
    write_output(data)

scrape()
