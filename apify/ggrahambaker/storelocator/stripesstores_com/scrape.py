import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import json

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    session = SgRequests()
    HEADERS = { 'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36' }

    locator_domain = 'https://stripesstores.com' 
    ext = '/locator/search/states'
    r = session.get(locator_domain + ext, headers = HEADERS)

    soup = BeautifulSoup(r.content, 'html.parser')

    states = soup.find('main', {'class': 'locations-wrapper'}).find_all('a')

    state_links = []
    for state in states:
        link = locator_domain + state['href']
        if '/ok' in link:
            continue
        
        state_links.append(link)

    city_list = []
    for state in state_links:
       
        r = session.get(state, headers = HEADERS)
        soup = BeautifulSoup(r.content, 'html.parser')
        cities = soup.find('main', {'class': 'locations-wrapper'}).find_all('a')
        for c in cities:
            city = str(locator_domain + c['href'])
            
            city_list.append(city)
            
    link_list = []
    for city in city_list:
        r = session.get(city, headers = HEADERS)
        soup = BeautifulSoup(r.content, 'html.parser')
        links = soup.find('main', {'class': 'locations-wrapper'}).find_all('div', {'class': 'btn-white'})
        
        for l in links:
            link = str(locator_domain + l.find('a')['href'])
            
            link_list.append(link)
        
    all_store_data = []
    for link in link_list:
        r = session.get(link, headers = HEADERS)
        soup = BeautifulSoup(r.content, 'html.parser')
        loc = json.loads(soup.find('script', {'type': 'application/ld+json'}).text)
        
        page_url = link
        location_name = loc['name']
        addy = loc['address']
        street_address = addy['streetAddress']
        city = addy['addressLocality']
        state = addy['addressRegion']
        zip_code = addy['postalCode']
        country_code = addy['addressCountry']
        
        coords = loc['geo']
        
        lat = coords['latitude']
        longit = coords['longitude']
        
        phone_number = loc['telephone'].replace('+1', '').strip()
        
        hours_obj = loc['openingHoursSpecification'][0]
        hours = 'Open 24 / 7'
        if hours_obj['opens'] != '00:00':

            if hours_obj['closes'] == '00:00':
                close = 'Midnight'
            hours = 'Open ' + hours_obj['opens'] + ' - ' + close
            
        store_number = '<MISSING>'
        location_type = '<MISSING>'
        
        store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code, 
                    store_number, phone_number, location_type, lat, longit, hours, page_url]
        
        all_store_data.append(store_data)

    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
