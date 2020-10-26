import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import unicodedata
import datetime
from sgrequests import SgRequests


session = SgRequests()

session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w',encoding="utf-8",newline="") as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    locator_domain = "https://www.choicehotels.com/rodeway-inn"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
        "X-Requested-With": "XMLHttpRequest",
        "content-type": "application/json;charset=UTF-8",
        "Accept": "application/json, text/plain, */*"
    }
    addresses=[]
    r= session.get("https://www.choicehotels.com/webapi/hotels/brand/RW?preferredLocaleCode=en-us&siteName=us",headers= headers).json()
    for value in r["hotels"]:
        store_number="<MISSING>"
        location_name= value["name"]
        if "line2" in value["address"]:
            street_address= value["address"]["line1"]+" "+ value["address"]["line2"]
        else:
            street_address =  value["address"]["line1"]
        city= value["address"]["city"]
        state = value["address"]["subdivision"]
        zipp = value["address"]["postalCode"]
        country_code = value["address"]["country"]
        location_type = value["brandName"]
        phone= value["phone"]
        latitude= value["lat"]
        longitude= value["lon"]
        hours_of_operation = "<MISSING>"
        page_url = "https://www.choicehotels.com/" + str(value["id"])
        if street_address in addresses:
            continue
        addresses.append(street_address)
        store = []
        store.append(locator_domain if locator_domain else '<MISSING>')
        store.append(location_name if location_name else '<MISSING>')
        store.append(street_address if street_address else '<MISSING>')
        store.append(city if city else '<MISSING>')
        store.append(state if state else '<MISSING>')
        store.append(zipp if zipp else '<MISSING>')
        store.append(country_code if country_code else '<MISSING>')
        store.append(store_number if store_number else '<MISSING>')
        store.append(phone if phone else '<MISSING>')
        store.append(location_type if location_type else '<MISSING>')
        store.append(latitude if latitude else '<MISSING>')
        store.append(longitude if longitude else '<MISSING>')
        store.append(hours_of_operation if hours_of_operation else '<MISSING>')
        store.append(page_url if page_url else "<MISSING>")
        yield store
        # print("===========",store)
    
def scrape():
    data = fetch_data()
    write_output(data)

scrape()

