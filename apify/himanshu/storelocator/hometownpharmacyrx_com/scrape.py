import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json



session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w', newline='') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    base_url= "https://hometownpharmacyrx.com"
    page = 0
    while True:

        json_data = session.get("https://hometownpharmacyrx.com/LocationSearch/GetLocations?lat=45.3467195&lng=-88.9365622&pageNumber="+str(page)).json()
        
        if json_data == []:
            break

        for data in json_data:

            location_name = data['Title']
            street_address = data['AddressLine1']

            if data['AddressLine2']:
                street_address += " " + data['AddressLine2']
            city = data['City']
            state = data['State']
            zipp = data['Zipcode']
            country_code = "US"
            store_number = data['Id']
            phone = data['Phone']
            location_type = "Pharmacy"
            lat = data['lat']
            lng = data['lng']
            hours = data['Hours'].replace("<br />","").replace("\r","").replace("\n"," ").replace("&nbsp;","").replace("This is NOT a walk in storefront location. Closed door only.","").strip()
            page_url = base_url + data['LocationUrl']

            store = []
            store.append(base_url)
            store.append(location_name)
            store.append(street_address)
            store.append(city)
            store.append(state)
            store.append(zipp)
            store.append(country_code)
            store.append(store_number)
            store.append(phone)
            store.append(location_type)
            store.append(lat)
            store.append(lng)
            store.append(hours)
            store.append(page_url)
            store = [x.replace("–","-") if type(x) == str else x for x in store]
            store = [str(x).strip() if x else "<MISSING>" for x in store]
            
            yield store
        
        page += 1

def scrape():
    data = fetch_data()
    write_output(data)


scrape()


