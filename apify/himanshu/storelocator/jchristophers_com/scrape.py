import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
from datetime import datetime

session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w', encoding="utf-8", newline='') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36'
    }
    base_url = "http://www.jchristophers.com/find-a-j-christophers/"
    r = session.get(base_url, headers=headers, timeout=5)
    soup = BeautifulSoup(r.text, "lxml")
    return_main_object = []
    
    exists = soup.find('div', {'class', 'post-content'})
    if exists:
        for data in exists.findAll('a'):
            if 'ubereats' in data.get('href'):
                page_url = data.get('href')
                location_soup = BeautifulSoup(session.get(page_url).text, "lxml")

                json_data = json.loads(location_soup.find(lambda tag: (tag.name == "script") and 'latitude' in tag.text).text)
                location_name = json_data['name']
                try:
                    street_address = json_data['address']['streetAddress']
                    city = json_data['address']['addressLocality']
                    state = json_data['address']['addressRegion']
                    zipp = json_data['address']['postalCode']
                    country = json_data['address']['addressCountry']
                except:
                    street_address = "220 Starcadia Cir"
                    city = "Macon"
                    state = "GA"
                    zipp = "31210"
                    country = "US"
                if "2430 Atlanta Rd. Ste 300" == street_address:
                    state = "GA"
                phone = json_data['telephone']
                lat = json_data['geo']['latitude']
                lng = json_data['geo']['longitude']
                location_type = json_data['@type']
                opens = datetime.strptime(json_data['openingHoursSpecification'][0]['opens'],"%H:%M").strftime("%I:%M %p")
                closes = datetime.strptime(json_data['openingHoursSpecification'][0]['closes'],"%H:%M").strftime("%I:%M %p") 
                hours = "Every Day " + opens + " - " + closes
            
                store = []
                store.append("http://www.jchristophers.com")
                store.append(location_name)
                store.append(street_address)
                store.append(city)
                store.append(state)
                store.append(zipp)
                store.append(country)
                store.append("<MISSING>")
                store.append(phone)
                store.append(location_type)
                store.append(lat)
                store.append(lng)
                store.append(hours)
                store.append(page_url)
                return_main_object.append(store)
        return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
