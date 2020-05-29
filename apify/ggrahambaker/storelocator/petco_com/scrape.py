import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import json

session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    locator_domain = 'https://www.petco.com/'
    url = 'https://stores.petco.com/'

    page = session.get(url)
    assert page.status_code == 200
    soup = BeautifulSoup(page.content, 'html.parser')

    main = soup.find('div', {'class':'tlsmap_list'})

    locs = main.find_all('a', {'class', 'gaq-link'})
    state_list = []
    for loc in locs:
        state_list.append(loc['href'])

    city_list = []

    for link in state_list:
        
        page = session.get(link)
        soup = BeautifulSoup(page.content, 'html.parser')
        main = soup.find('div', {'class':'map-list'})
        cities = main.find_all('a', {'class', 'gaq-link'})
        for city in cities:
            link = city['href']
            city_list.append(link)
        
    link_list = []
    for link in city_list:
        page = session.get(link)
        soup = BeautifulSoup(page.content, 'html.parser')
        locs = soup.find_all('div', {'class':'map-list-item'})
        for loc in locs:
            link = loc.find('a')['href']
            link_list.append(link)

    all_store_data = []
    for i, link in enumerate(link_list):
        page = session.get(link)
        soup = BeautifulSoup(page.content, 'html.parser')
        loc_jsons = soup.find_all('script')
        for loc in loc_jsons:
            if "@context" in loc.text:
                loc_json = json.loads(loc.text)[0]

        coords = loc_json['geo']
        lat = coords['latitude']
        longit = coords['longitude']
        
        addy = loc_json['address']
        phone_number = addy['telephone']
        street_address = addy['streetAddress']
        city = addy['addressLocality']
        state = addy['addressRegion']
        zip_code = addy['postalCode']

        hours = loc_json['openingHours']

        location_name = loc_json['name'].replace('Welcome to your Petco in ', '').replace('Welcome to your ', '').replace('!', '').strip()
        country_code = 'US'
        page_url = link
        location_type = soup.find('span', {'class':'location-name'}).text
        store_number = link.split('-')[-1].replace('.html', '')
        
        store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code,
                        store_number, phone_number, location_type, lat, longit, hours, page_url]

        all_store_data.append(store_data)
                
    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
