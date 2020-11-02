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
    base_url ="https://www.chevron.com/"
    return_main_object=[]
    coords=sgzip.coords_for_radius(50)
    output=[]
    for cd in coords:
        r = session.get("https://www.chevronwithtechron.com/webservices/ws_getChevronTexacoNearMe_r2.aspx?lat="+cd[0]+"&lng="+cd[1]+"&brand=chevronTexaco&radius=35").json()
        for loc in r['stations']:
            store=[]
            name=loc['name']
            address=loc['address']
            city=loc['city']
            state=loc['state']
            zip=loc['zip']
            country="US"
            storeno=loc['id']
            phone=loc['phone']
            lat=loc['lat']
            lng=loc['lng']
            hour=''
            page_url=''
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
            store.append(hour if hour.strip() else "<MISSING>")
            store.append(page_url if page_url else "<MISSING>")
            adrr =name+' '+address + ' ' + city + ' ' + state + ' ' + zip
            if adrr not in output:
                output.append(adrr)
                yield store
    return return_main_object
def scrape():
    data = fetch_data()
    write_output(data)
scrape()
