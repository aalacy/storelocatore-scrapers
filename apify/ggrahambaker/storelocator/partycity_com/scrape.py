import csv
import json
from sgrequests import SgRequests
from bs4 import BeautifulSoup

from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('partycity_com')


def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    
    locator_domain = 'partycity.com/'
    url = 'https://stores.partycity.com/us/'

    user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36'
    HEADERS = {'User-Agent' : user_agent}

    session = SgRequests()
    req = session.get(url, headers = HEADERS)
    base = BeautifulSoup(req.text,"lxml")

    state_list = []
    main = base.find(class_='tlsmap_list')
    states = main.find_all(class_='gaq-link')
    for state in states:
        state_list.append(state['href'])
        
    city_list = []
    for state in state_list:
        req = session.get(state, headers = HEADERS)
        base = BeautifulSoup(req.text,"lxml")

        main = base.find(class_='tlsmap_list')
        cities = main.find_all(class_='gaq-link')
        for city in cities:
            city_list.append(city['href'])
            
    link_list = []
    logger.info("Processing " + str(len(city_list)) + " city links ..")
    for city in city_list:
        req = session.get(city, headers = HEADERS)
        base = BeautifulSoup(req.text,"lxml")
        
        locs = base.find_all(class_='map-list-item')
        for loc in locs:
            link = loc.a['href']
            link_list.append(link)

    all_store_data = []
    logger.info("Processing " + str(len(link_list)) + " final links ..")
    for link in link_list:
        r = session.get(link, headers=HEADERS)
        soup = BeautifulSoup(r.content, 'lxml')

        country_code = "US"
        
        info = soup.find('script', {'type': 'application/ld+json'}).text
        loc = json.loads(info)[0]

        addy = loc['address']
        
        street_address = addy['streetAddress'].strip()
        city = addy['addressLocality'].strip()
        state = addy['addressRegion'].strip()
        zip_code = addy['postalCode'].strip()
        
        phone_number = addy['telephone'].strip()
        
        coords = loc['geo']
        lat = coords['latitude'].strip()
        longit = coords['longitude'].strip()
        
        hours = loc['openingHours'].strip()
        
        location_name = loc['mainEntityOfPage']['headline'].strip()
        try:
            store_number = link.split("pc")[-1].split(".")[0]
        except:
            store_number = '<MISSING>'

        location_type = '<MISSING>'
        page_url = link
        store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code, 
                    store_number, phone_number, location_type, lat, longit, hours, page_url]

        all_store_data.append(store_data)

    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
