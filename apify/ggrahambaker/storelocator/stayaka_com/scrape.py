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

    locator_domain = 'https://www.stayaka.com/'
    ext = 'locations'

    response = session.get(locator_domain + ext, headers = HEADERS)

    soup = BeautifulSoup(response.content, 'html.parser')

    link_list = []
    main = soup.find('div', {'class': 'page-content'})
    links = main.find_all('a')
    for link in links:
        if 'aka' not in link['href']:
            continue
        if 'http' not in link['href']:
            l = locator_domain + link['href'][1:]
        else:
            l = link['href']
        link_list.append(l)

    all_store_data = []
    for link in link_list:
        response = session.get(link, headers = HEADERS)

        soup = BeautifulSoup(response.content, 'html.parser')
        cont = json.loads(soup.find('script', {'type': 'application/ld+json'}).text)
        location_name = cont['name']
        page_url = cont['url']
        if 'Tribeca' in location_name:
            phone_number = '212.587.7000'
        elif 'West Hollywood' in location_name:
            phone_number = '310.626.0888'
        else:
            phone_number = cont['telephone']
        addy = cont['address']

        if 'Wall Street' in location_name:
            street_address = '84 William St.'
        elif 'Tribeca' in location_name:
            street_address = '85 W Broadway'
        elif 'Beverly Hills' in location_name:
            street_address = '155 N. Crescent Drive'
        elif 'University City' in location_name:
            street_address = '2929 Walnut St.'
        elif 'White House' in location_name:
            street_address = '1710 H Street NW.'
        elif 'Marylebone' in location_name:
            break 
        elif 'West Hollywood' in location_name:
            street_address = '8500 West Sunset Boulevard'
        elif 'Rittenhouse' in location_name:
            street_address = '135 South 18th St'
        else:
            street_address = addy['streetAddress']
        
        city = addy['addressLocality']
        state = addy['addressRegion']
        zip_code = addy['postalCode']

        lat = cont['geo']['latitude']
        longit = cont['geo']['longitude']
        country_code = 'US'
        store_number = '<MISSING>'
        location_type = '<MISSING>'
        hours = '<MISSING>'
        
        store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code, 
                    store_number, phone_number, location_type, lat, longit, hours, page_url]

        all_store_data.append(store_data)

    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
