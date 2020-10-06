import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
import re
import json
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
        state = data['address'][0]['state']
        zipp = data['address'][0]['zip'].replace("  "," ")
        country_code = data['address'][0]['country']
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
def scrape():
    data = fetch_data()
    write_output(data)
scrape()