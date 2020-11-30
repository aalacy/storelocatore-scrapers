import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json

session = SgRequests()
def write_output(data):
    with open('data.csv', mode='w', encoding="utf-8",newline='') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)
def fetch_data():
    addresses = []
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36',
        'Accept': 'application/json, text/plain, */*',
    }
    base_url = "https://www.davita.com/"
    states = ["AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DC", "DE", "FL", "GA", 
          "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD", 
          "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ", 
          "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC", 
          "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY"]
    locator_domain = base_url
    location_name = ""
    street_address = ""
    city = ""
    state = ""
    zipp = ""
    country_code = "US"
    store_number = ""
    phone = ""
    location_type = ""
    latitude = ""
    longitude = ""
    hours_of_operation = ""
    for state in states:
        location_url = "https://www.davita.com/api/find-a-center?location="+state+"&lat=32.3182314&lng=-86.902298"
        r = session.get(location_url, headers=headers, verify=False).json()
        if r['locations'] != None:
            for data in r['locations']:
                location_name = data['facilityname']
                street_address = (data['address']['address1'] +" "+ str(data['address']['adress2'])).strip()
                city = data['address']['city']
                state = data['address']['state']
                zipp = data['address']['zip']
                latitude = data['address']['latitude']
                longitude = data['address']['longitude']
                store_number = data['facilityid']
                phone = data['phone']
                page_url = "https://www.davita.com/locations/"+str(state.lower())+"/"+str(city.lower())+"/"+str(data['address']['address1'].replace(" ","-").lower())+"--"+str(store_number)
                store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
                        store_number, phone, location_type, latitude, longitude, hours_of_operation, page_url]
                if str(store[1]) in addresses:
                    continue
                addresses.append(str(store[1]))
                store = [x.strip() if x else "<MISSING>" for x in store]
                yield store
            else:
                pass
def scrape():
    data = fetch_data()
    write_output(data)
scrape()
