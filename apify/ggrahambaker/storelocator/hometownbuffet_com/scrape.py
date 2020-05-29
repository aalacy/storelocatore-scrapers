import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
from sgselenium import SgSelenium
import json

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def addy_ext(addy):
    addy = addy.split(',')
    city = addy[0]
    state_zip = addy[1].strip().split(' ')
    state = state_zip[0]
    zip_code = state_zip[1]
    return city, state, zip_code

def fetch_data():
    session = SgRequests()
    HEADERS = { 'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36' }
    locator_domain = 'http://www.hometownbuffet.com/'
    all_store_data = []

    map_url = 'http://www.hometownbuffet.com/locator/'
    driver = SgSelenium().chrome()
    driver.get(map_url)

    map_data = driver.execute_script('return usahtml5map_map_cfg_0')['map_data']

    skip_states = set()
    for state, info in map_data.items():
        if info['comment'] == '':
            skip_states.add(info['id'])

    driver.quit()
    for i in range(50):
        url = 'http://www.hometownbuffet.com/index.php?usahtml5map_get_state_info=' + str(i) + '&map_id=0'    
        if i in skip_states:
            continue
        r = session.get(url, headers = HEADERS)
        soup = BeautifulSoup(r.content, 'html.parser')
        for div in soup.find_all('div'):
            locations = div.find_all('i', {'class': 'icon-location'})
            
            clocks = div.find_all('i', {'class': 'icon-clock'}) 
            if len(locations) == 0:
                continue

            location_type = div.find('div').text
            addy_br = div.find('br')
            street_address = addy_br.previous.strip()
            city, state, zip_code = addy_ext(addy_br.next.strip())
            
            location_name = city
 
            google_href = div.find('a')['href']
            coords = google_href[google_href.find('@') + 1:].split(',')

            lat = coords[0]
            longit = coords[1]
            hours_split = div.findNext('p').prettify().split('\n')
            if len(hours_split) == 6:

                hours_split = div.findNext('p').findNext('p').prettify().split('\n')
      
            hours = ''
            for h in hours_split:
                if '<' in h:
                    continue
                if 'HOURS' in h:
                    continue
                
                hours += h + ' '
                
            hours = hours.strip()
            phone_number = div.find('i', {'class': 'icon-call'}).next.strip()
            
            country_code = 'US'
            store_number = '<MISSING>'
            page_url = '<MISSING>'
            
            store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code, 
                        store_number, phone_number, location_type, lat, longit, hours, page_url]

            all_store_data.append(store_data)
            
    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
