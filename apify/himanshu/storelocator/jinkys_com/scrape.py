import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
import re
import json
session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w',encoding="utf-8", newline='') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36'
    }

    soup = bs(session.get("http://www.jinkys.com/",headers=headers).text,"lxml")
    json_data = json.loads(soup.find(lambda tag:(tag.name == "script") and '"lat"' in tag.text).text)['preloadQueries'][0]
    # for data in json_data:
    for loc in json_data['data']['restaurant']['locations']:
        location_name = loc['name']
        street_address = loc['streetAddress']
        city = loc['city']
        state = loc['state']
        zipp = loc['postalCode']
        country_code = loc['country']
        store_number = loc['id']
        phone = loc['phone']
        location_type = loc['__typename'].replace("Location","").strip()
        latitude = loc['lat']
        longitude = loc['lng']
        hours = " ".join(loc['schemaHours'])

        store = []
        store.append("http://www.jinkys.com")
        store.append(location_name)
        store.append(street_address)
        store.append(city)
        store.append(state)
        store.append(zipp)
        store.append(country_code)
        store.append(store_number)
        store.append(phone)
        store.append(location_type)
        store.append(latitude)
        store.append(longitude)
        store.append(hours)
        store.append("https://www.jinkys.com/menu-"+str(loc['slug']))
        store = [str(x).strip() if x else "<MISSING>" for x in store]
        yield store

def scrape():
    data = fetch_data()
    write_output(data)

scrape()

