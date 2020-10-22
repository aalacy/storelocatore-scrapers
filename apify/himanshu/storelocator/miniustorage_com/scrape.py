import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
import re
import json
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
    headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.75 Safari/537.36',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9'
    }

    base_url = "https://www.miniustorage.com/"
    r = session.get("https://www.miniustorage.com/locations/",headers=headers)
    soup = bs(r.text,'html5lib')
    jd = json.loads(soup.find_all("script",{"type":"application/ld+json"})[1].text)['location']
    for val in jd:
        location_name = val['name'].replace("&#8211;","-")
        street_address = val['address']['streetAddress']
        city = val['address']['addressLocality']
        state = val['address']['addressRegion']
        zipp = val['address']['postalCode']
        phone = val['telephone']
        location_type = val['@type']
        latitude = val['geo']['latitude']
        longitude = val['geo']['longitude']
        page_url = "https://www.miniustorage.com/location/USA/"+state+"/"+city.replace(" ","-")+"/"+city.lower().replace(" ","-")+"/"

        store = []
        store.append(base_url if base_url else "<MISSING>")
        store.append(location_name if location_name else "<MISSING>") 
        store.append(street_address if street_address else "<MISSING>")
        store.append(city if city else "<MISSING>")
        store.append(state if state else "<MISSING>")
        store.append(zipp if zipp else "<MISSING>")
        store.append( "US")
        store.append("<MISSING>") 
        store.append(phone if phone else "<MISSING>")
        store.append(location_type)
        store.append(latitude if latitude else "<MISSING>")
        store.append(longitude if longitude else "<MISSING>")
        store.append("<MISSING>")
        store.append(page_url if page_url else "<MISSING>")
        yield store
def scrape():
    data = fetch_data()
    write_output(data)
scrape()

