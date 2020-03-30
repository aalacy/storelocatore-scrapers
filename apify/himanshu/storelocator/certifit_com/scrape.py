import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
import sgzip

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
    base_url = "http://www.certifit.com"
    zps=sgzip.for_radius(50)
    output = []
    for zp in zps:
        r = session.get(base_url+"/store/site_market_area/enterprise/readwherelikezipcode/"+str(zp)).json()
        for st in r:
            try:
                page_url=base_url+"/store/site_info/enterprise/readwherecode/"+st['SiteCode']
                r1 = session.get(page_url).json()
                for loc in r1:
                    hour=loc['Hours'].replace('<br/>',' ').replace('<br>',' ').strip()
                    address=loc['Address']
                    city=loc['City']
                    lat=loc['Latitude']
                    lng=loc['Longitude']
                    name=loc['Name']
                    storeno=''
                    zip=loc['Zip']
                    country="US"
                    state=loc['State']
                    phone=loc['Phone']
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
                    store.append("<MISSING>")
                    store.append(lat if lat else "<MISSING>")
                    store.append(lng if lng else "<MISSING>")
                    store.append(hour if hour else "<MISSING>")
                    store.append(page_url if page_url else "<MISSING>")
                    addr=name+' '+address+' '+city+' '+state+' '+zip
                    if addr not in output:
                        output.append(addr)
                        yield store
            except:
                continue

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
