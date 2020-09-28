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
    headers = {
        "user-agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36"
    }
    r = session.get("http://malbeccuisine.com",headers=headers)
    soup = BeautifulSoup(r.text,"lxml")
    for location in soup.find_all("script",{'type':"application/json"})[-3]:
        json_data = json.loads(location)
        j =  json_data['preloadQueries']
        for k in j :
            try:
                h = k['data']['restaurant']['locations']
            except:
                continue
            for g in h:
                d = (g['socialHandles'])
                for f in d:
                    url = (f['url'])
                    phone = "("+g['phone'][0:3]+") "+g['phone'][3:6]+"-"+g['phone'][6:10]
                    store = []
                    store.append("http://malbeccuisine.com")
                    store.append(g['name'])
                    store.append(g['streetAddress'])
                    store.append(g['city'])
                    store.append(g['state'])
                    store.append(g['postalCode'])
                    store.append("US")
                    store.append("<MISSING>")
                    store.append(phone)
                    store.append("malbec argentinean cuisine")
                    store.append(g['lat'])
                    store.append(g['lng'])
                    store.append(str(g['schemaHours']).replace("'","").replace("[","").replace("]","").replace("'",""))
                    store.append(url)
                    yield store
def scrape():
    data = fetch_data()
    write_output(data)
scrape()
