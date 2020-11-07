import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json

from sglogging import SgLogSetup
logger = SgLogSetup().get_logger('spencersonline_com')
session = SgRequests()
def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        for row in data:
            writer.writerow(row)
def fetch_data():
    addresses = []
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
    }
    base_url = "https://www.spencersonline.com/custserv/locate_store.cmd"
    r = session.get(base_url, headers=headers)
    soup = BeautifulSoup(r.text,"lxml")
    tag_store = soup.find(lambda tag: (tag.name == "script") and "var allStores" in  tag.text.strip())
    m = (tag_store.text)
    for i in range(1,670):
        store_number = (m.split("store.STORE_NUMBER = '")[i].split("store.ADDRESS_LINE_1")[0].replace("';","").strip().lstrip())
        street_address = (m.split("store.ADDRESS_LINE_2 = '")[i].split("store.CITY = '")[0].replace("';","").strip())
        latitude = (m.split("store.LATITUDE = '")[i].split("store.LONGITUDE = '")[0].replace("';","").strip())
        longitude = (m.split("store.LONGITUDE = '")[i].split("store.STORE_STATUS = '")[0].replace("';","").strip())
        zipp = (m.split("store.ZIP_CODE = '")[i].split("store.PHONE = '")[0].replace("';","").strip())
        phone = (m.split("store.PHONE = '")[i].split("store.LATITUDE = '")[0].replace("';","").strip())
        country_code = (m.split("store.COUNTRY_CODE ='")[i].split("store.ZIP_CODE = '")[0].replace("';","").strip())
        state = (m.split("store.STATE ='")[i].split("store.COUNTRY_CODE =")[0].replace("';","").strip())
        city = (m.split("store.CITY = '")[i].split("store.STATE ='")[0].replace("';","").strip())
        location_name = (m.split("store.STORE_NAME = '")[i].split("store.STORE_NUMBER = '")[0].replace("';","").strip())
        hours_of_operation = (m.split("store.STORE_STATUS = '")[i].split("';")[0].strip().replace("Coming Soon","<MISSING>"))
        STORE_ID = (m.split("store.STORE_ID = '")[i].split("store.STORE_NAME = '")[0].replace("';","").strip())
        page_url = "https://www.spencersonline.com/store/"+str(location_name.strip().lstrip().replace(" ","-"))+"/"+str(STORE_ID.strip().lstrip())+".uts"
        ca_zip_list = re.findall(r'[A-Z]{1}[0-9]{1}[A-Z]{1}\s*[0-9]{1}[A-Z]{1}[0-9]{1}', str(zipp))
        us_zip_list = re.findall(re.compile(r"\b[0-9]{5}(?:-[0-9]{4})?\b"), str(zipp))
        if len(zipp)==5:
            zipp = zipp
            country_code = "US"
        elif len(zipp)==6:
            zipp = zipp
            country_code = "CA"
        else:
            zipp = zipp[:5]+"-"+zipp[5:]
            country_code = "US" 
        location_type = "store"
        if "07073" in zipp:
            location_type = "<MISISNG>" 
        store = []
        store.append("https://www.spencersonline.com/")
        store.append(location_name if location_name else "<MISSING>") 
        store.append(street_address if street_address else "<MISSING>")
        store.append(city if city else "<MISSING>")
        store.append(state if state else "<MISSING>")
        store.append(zipp if zipp else "<MISSING>")
        store.append(country_code)
        store.append(store_number if store_number else "<MISSING>") 
        store.append(phone if phone else "<MISSING>")
        store.append(location_type if location_type else  "<MISSING>")
        store.append(latitude if latitude else "<MISSING>")
        store.append(longitude if longitude else "<MISSING>")
        store.append("<MISSING>")
        store.append(page_url)
        if store[2] in addresses:
            continue
        addresses.append(store[2])
        yield store
def scrape():
    data = fetch_data()
    write_output(data)
scrape()