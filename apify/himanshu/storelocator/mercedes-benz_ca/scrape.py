import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
import re
import json
import html5lib
session = SgRequests()
def write_output(data):
    with open('data.csv', mode='w', newline='') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        for row in data:
            writer.writerow(row)
def fetch_data(): 
    base_url = "https://www.mercedes-benz.ca"
    json_data = session.get("https://nafta-service.mbusa.com/api/dlrsrv/v1/ca/search?zip=A1A1A1&start=1&count=100&filter=mbdealer").json()['results']
    for data in json_data:
        location_name = data['name']
        street_address = (data['address'][0]['line1']+ str(data['address'][0]['line2'])).strip()
        city = data['address'][0]['city']
        state = data['address'][0]['state'].upper()
        zipp = data['address'][0]['zip'].replace("  "," ")
        country_code = data['address'][0]['country'].upper()
        store_number = data['id']
        phone = data['contact'][0]['value']
        lat = data['address'][0]['location']['lat']
        lng = data['address'][0]['location']['lng']
        location_type = data['type']
        if data['url']:
            page_url = data['url']
        else:
            page_url = "http://www.mbofcovington.com/"
        if "http://www.loeber.mercedesdealer.com" in data['url']:
            page_url = "https://www.loebermercedes.com/"
        store = []
        store.append(base_url)
        store.append(location_name)
        store.append(street_address.replace('None',''))
        store.append(city)
        store.append(state)
        store.append(zipp)   
        store.append(country_code)
        store.append(store_number)
        store.append(phone)
        store.append(location_type)
        store.append(lat)
        store.append(lng)
        store.append("<INACCESSIBLE>")
        store.append(page_url)    
        store = [str(x).encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]
        yield store
    json_data = session.get("https://nafta-service.mbusa.com/api/dlrsrv/v1/ca/search?zip=A1A1A1&start=1&count=100&filter=mbdealer").json()['aoiDealer']
    location_name = json_data['name']
    store_number = json_data['id']
    for data in json_data['address']:
        street_address = (data['line1']+ str(data['line2'])).strip()
        city = data['city']
        state = data['state'].upper()
        zipp = data['zip'].replace("  "," ")
        country_code = data['country'].upper()
        phone = "(709) 738-2369"
        lat = data['location']['lat']
        lng = data['location']['lng']
        location_type = data['type']
        store = []
        store.append(base_url)
        store.append(location_name)
        store.append(street_address.replace('None',''))
        store.append(city)
        store.append(state)
        store.append(zipp)   
        store.append(country_code)
        store.append(store_number)
        store.append(phone)
        store.append(location_type)
        store.append(lat)
        store.append(lng)
        store.append("<INACCESSIBLE>")
        store.append("https://www.mercedes-benz-stjohns.ca") 
        store = [str(x).encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]
        yield store
    json_data = session.get("https://www.mercedes-benz-oregans.ca/")
    soup = bs(json_data.text, "html5lib")
    mp = (soup.find_all("script",{"type":"application/ld+json"})[-1]).text
    json_data = json.loads(mp)
    location_name = json_data['name']
    street_address = json_data['address']['streetAddress']
    city = json_data['address']['addressLocality']
    state = json_data['address']['addressRegion']
    zipp = json_data['address']['postalCode']
    country_code = json_data['address']['addressCountry']
    location_type = json_data['@type']
    phone = json_data['telephone']
    store = []
    store.append(base_url)
    store.append(location_name)
    store.append(street_address.replace('None',''))
    store.append(city)
    store.append(state)
    store.append(zipp)   
    store.append(country_code)
    store.append("<MISSING>")
    store.append(phone)
    store.append(location_type)
    store.append("44.6626477")
    store.append("-63.6166623")
    store.append("<INACCESSIBLE>")
    store.append("https://www.mercedes-benz-oregans.ca")   
    store = [str(x).encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]
    yield store
def scrape():
    data = fetch_data()
    write_output(data)
scrape()