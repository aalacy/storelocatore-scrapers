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

    locator_domain = 'https://www.prohealthcare.org/'
    ext = 'locations/'
    r = session.get(locator_domain + ext, headers = HEADERS)

    soup = BeautifulSoup(r.content, 'html.parser')

    pages = soup.find('div', {'class': 'Pagination'}).find_all('option')
    links = [locator_domain + page['value'][2:] for page in pages]

    all_store_data = []
    for link in links:
        r = session.get(link, headers = HEADERS)
        soup = BeautifulSoup(r.content, 'html.parser')
        
        locs = soup.find_all('script', {'type': 'application/ld+json'})
        links = soup.find_all('a', {'class': 'Name'})
        #street_addresses = soup.find_all('span', {'class': 'street-address'})

        for i, loc in enumerate(locs):
           
            page_url = locator_domain[:-1] + links[i]['href']
            #street_address = street_addresses[i].text
            
            info = json.loads(loc.text)
            
            location_name = info['name']
            phone_number = info['telephone'].replace('+1-', '')
            addy = info['address']
            street_addy = addy['streetAddress']
            street_addy = street_addy.split(',')
            if len(street_addy) == 1:
                street_address = street_addy[0].strip()
               
            else:
                if 'Suite' in street_addy[1]:
                    street_address = street_addy[0].strip()
                else:
                    street_address = street_addy[1].strip()

            city = addy['addressLocality']
            state = addy['addressRegion']
            zip_code = addy['postalCode']
            coords = info['geo']
            lat = coords['latitude']
            longit = coords['longitude']
            
            country_code = 'US'
            store_number = '<MISSING>'
            location_type = '<MISSING>'
            if 'openingHoursSpecification' not in info:
                hours = '<MISSING>'
            else:
                hours = ''
                for day_info in info['openingHoursSpecification']:
                    start = day_info['opens']
                    end = day_info['closes']
                    day_of_week = day_info['dayOfWeek'].replace('http://schema.org/', '').strip()
                    hours += day_of_week + ' ' + start + ' ' + end + ' '
                    
                hours = hours.strip()
                
            store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code, 
                        store_number, phone_number, location_type, lat, longit, hours, page_url]

            all_store_data.append(store_data)

    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
