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
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    base_url = "https://www.mycornerstonedentist.com/dentist-offices/"
    r = session.get(base_url)
    soup = BeautifulSoup(r.text,"lxml")
    return_main_object = []
    main=soup.find_all("script",{"type":"text/javascript"})
    for script in main:
        if re.search('var map_data',script.text):
            data=script.text.split('var map_data = ')[1].split('};')[0]+"}"
            m=json.loads(data)['offices']
            for val in m:
                store = []
                city=m[val]['city_state_zip'].split(',')[0].strip()
                state=m[val]['city_state_zip'].split(',')[1].strip().split(' ')[0].strip()
                zip=m[val]['city_state_zip'].split(',')[1].strip().split(' ')[1].strip()
                store.append("https://www.mycornerstonedentist.com")
                store.append(m[val]['name'].replace('<br />','').strip())
                store.append(m[val]['street_address'])
                store.append(city)
                store.append(state)
                store.append(zip)
                store.append('US')
                store.append(m[val]['ID'])
                try:
                    store.append(m[val]['phone'])
                except:
                    store.append("<MISSING>")
                store.append("mycornerstonedentist")
                store.append(m[val]['latitude'])
                store.append(m[val]['longitude'])
                store.append("<MISSING>")
                return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
