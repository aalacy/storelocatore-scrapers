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
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation" , "page_url"])
        # Body
        for row in data:
            writer.writerow(row)
def fetch_data():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
    }
    base_url= "https://api.marksandspencer.com/v1/stores?apikey=aVCi8dmPbHgHrdCv9gNt6rusFK98VokK&jsonp=angular.callbacks._1&latlong=51.49919128417969,-0.09428299963474274&limit=3000&radius=5000000"
    r = session.get(base_url, headers=headers)
    soup= BeautifulSoup(r.text,"lxml")
    data = (soup.text.split(");")[0].split("callbacks._1(")[1])
    json_data = json.loads(data)
    k = (json_data['results'])

    for d in k:
        location_name = (d['name'])
        street_address = d['address']['addressLine2']
        country_code = d['address']['country']
        city= d['address']['city']
        zipp = d['address']['postalCode']
        state = d['address']['isoTwoCountryCode']
        if 'phone' in d:
            phone = (d['phone'].strip())
        else:
            phone = ("MISSING")
        latitude =  d['coordinates']['latitude']
        longitude =  d['coordinates']['longitude']
        store_number = d['id']
        location_type = d['storeType']
        url = "https://www.marksandspencer.com/MSResStoreFinderGlobalBaseCmd?storeId=10151&langId=-24&SAPStoreId="+str(store_number)+"&extid=local"
        hours_of_operation =''
        h1  = (d['coreOpeningHours'])
        hours_of_operation = (str(h1).replace("'","").replace("{","").replace("}","").replace("[","").replace("]","").replace("day: ","").replace(", close:"," -").replace(" open:","-").replace("y,","y ")) 
        store = []
        store.append("https://www.marksandspencer.com/")
        store.append(location_name if location_name else '<MISSING>')
        store.append(street_address if street_address else '<MISSING>')
        store.append(city if city else '<MISSING>')
        store.append(state.upper() if state else '<MISSING>')
        store.append(zipp if zipp else '<MISSING>')
        store.append(country_code if country_code else '<MISSING>')
        store.append(store_number if store_number else '<MISSING>')
        store.append(phone if phone else '<MISSING>')
        store.append(location_type if location_type else '<MISSING>')
        store.append(latitude if latitude else '<MISSING>' )
        store.append(longitude if longitude else '<MISSING>')
        store.append(hours_of_operation if hours_of_operation else '<MISSING>' )
        store.append(url)
        if "United Kingdom" in country_code:
            yield store
def scrape():
    data = fetch_data()
    write_output(data)

scrape()
