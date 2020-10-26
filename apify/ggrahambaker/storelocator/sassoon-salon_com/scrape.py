import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup

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
    locator_domain = 'https://www.sassoon-salon.com/'
    ext = 'en/salon/us/salons-(1)'
    r = session.get(locator_domain + ext, headers = HEADERS)

    soup = BeautifulSoup(r.content, 'html.parser')

    locs = soup.find('div', {'id': 'NorthAmerica'}).find_all('a', {'class': 'tile__link'})
    link_list = [locator_domain[:-1] + loc['href'] for loc in locs]

    all_store_data = []
    for link in link_list:
        print(link)
        r = session.get(link, headers = HEADERS)
        soup = BeautifulSoup(r.content, 'html.parser')
        location_name = soup.find('h1', {'class': 'hero-salon__title'}).text
        
        phone_number = soup.find('a', {'class': 'hero-salon__phone-link'}).text
        
        coords = soup.find('div', {'class': 'js-map-location'})['data-coords'].split(',')
        lat = coords[0]
        longit = coords[1]
        addy = soup.find('span', {'class': 'hero-salon__location'}).prettify().split('\n')
        
        addy_arr = []
        for a in addy:
            if '<' in a:
                continue
            if a == '':
                continue
            addy_arr.append(a.strip())
            
        if len(addy_arr) == 3:
            if '3333' in addy_arr[0]:
                street_address = addy_arr[0] + ' ' + addy_arr[1]
                city, state, zip_code = addy_ext(addy_arr[2])
            else:
                street_address = addy_arr[1]
                city, state, zip_code = addy_ext(addy_arr[2])
                
            country_code = 'US'
        elif len(addy_arr) == 4:
            street_addrss = addy_arr[1]
            city, state, zip_code = addy_ext(addy_arr[3])
            country_code = 'US'
        else:
            if '122 SCOLLARD STREET' in addy_arr[0]:
                street_address = addy_arr[0] 
                can_addy = addy_arr[1].replace('\xa0', ' ').split(' ')
                city = can_addy[0].replace(',', '')
                state = can_addy[1]
                zip_code = can_addy[2] + ' ' + can_addy[3]
                
                city, state, zip_code = addy_ext(addy_arr[1])
                country_code = 'CA'
            else:
                street_address = addy_arr[0] 
                city, state, zip_code = addy_ext(addy_arr[1])
                country_code = 'US'
                
        store_number = '<MISSING>'
        location_type = '<MISSING>'
        
        trs = soup.find_all('tr', {'class': 'salon-opening-hours__markup-tr'})
        hours = ''
        for tr in trs:
            cols = tr.find_all('td')
            for col in cols:
                hours += col.text + ' '
                
        hours = hours.strip()
        page_url = link
        
        store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code, 
                    store_number, phone_number, location_type, lat, longit, hours, page_url]

        all_store_data.append(store_data)
    
    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
