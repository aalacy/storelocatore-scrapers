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

    locator_domain = 'http://goldenchick.com/' 
    url = 'http://locations.goldenchick.com/'
    r = session.get(url, headers = HEADERS)

    soup = BeautifulSoup(r.content, 'html.parser')

    loc_links = soup.find('div', {'id': 'parent_container_two'}).previous_sibling.previous_sibling.find_all('a')

    state_list = []
    for loc in loc_links:
        state_list.append(loc['href'])

    city_list = [] 
    for link in state_list:
        r = session.get(link, headers = HEADERS)
        soup = BeautifulSoup(r.content, 'html.parser')
        loc_links = soup.find('div', {'id': 'parent_container_two'}).previous_sibling.previous_sibling.find_all('a')

        for loc in loc_links:        
            if len(loc['href'].split('/')) == 6:                
                city_list.append(loc['href'])
            
    link_list = []
    for link in city_list:
        r = session.get(link, headers = HEADERS)
        soup = BeautifulSoup(r.content, 'html.parser')
        loc_links = soup.find('div', {'id': 'parent_container_two'}).previous_sibling.previous_sibling.find_all('a')
        
        for loc in loc_links:
            if len(loc['href'].split('/')) == 7:                
                link_list.append(loc['href'])

    all_store_data = []
    for link in link_list:
        r = session.get(link, headers = HEADERS)
        soup = BeautifulSoup(r.content, 'html.parser')
        
        location_name = soup.find('meta', {'property': 'og:title'})['content']

        street_address = soup.find('meta', {'property': 'business:contact_data:street_address'})['content']
        city = soup.find('meta', {'property': 'business:contact_data:locality'})['content']
        state = soup.find('meta', {'property': 'business:contact_data:region'})['content']
        zip_code = soup.find('meta', {'property': 'business:contact_data:postal_code'})['content']
        country_code = soup.find('meta', {'property': 'business:contact_data:country_name'})['content']
        phone_number = soup.find('meta', {'property': 'business:contact_data:phone_number'})['content']
        
        lat = soup.find('meta', {'property': 'place:location:latitude'})['content']
        longit = soup.find('meta', {'property': 'place:location:longitude'})['content']
        
        hours_divs = soup.find('div', {'id': 'col_one'}).find_all('div')
        hours = ''
        for day in hours_divs:
            if 'Holiday' in day.text:
                break
            hours += day.text.strip() + ' '

        hours = ' '.join( hours.split())
        store_number = link.split('/')[-2]
        location_type = '<MISSING>'
        page_url = link
        country_code = 'US'
        store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code, 
                    store_number, phone_number, location_type, lat, longit, hours, page_url]

        all_store_data.append(store_data)

    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
