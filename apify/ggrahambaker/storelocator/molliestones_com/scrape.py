import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
from sgselenium import SgSelenium

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
    driver = SgSelenium().chrome()

    session = SgRequests()
    HEADERS = { 'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36' }

    locator_domain = 'https://www.molliestones.com/' 
    ext = 'StoreLocator/State/?State=CA'
    r = session.get(locator_domain + ext, headers = HEADERS)

    soup = BeautifulSoup(r.content, 'html.parser')
    links = soup.find('div', {'id': 'StoreLocator'}).find_all('td', {'align': 'right'})
    link_list = []
    for l in links:
        if l.text.strip() == 'View':
            link_list.append(l.find('a')['href'])

    all_store_data = []
    for link in link_list:
        r = session.get(link, headers = HEADERS)
        soup = BeautifulSoup(r.content, 'html.parser')

        driver.get(link)
        lat, longit = '', ''
        source = str(driver.page_source)
        for line in source.splitlines():
            if 'initializeMap(' in line:                
                coords = line.strip().split('(')[1].split(')')[0].replace('"', '').strip().split(',')
                lat = coords[0]
                longit = coords[1]
                
        if lat == '':
            lat = '<MISSING>'
            longit = '<MISSING>'
        
        location_name = soup.find('h3').text

        addy = soup.find('p', {'class': 'Address'}).prettify().split('\n')
        r_addy = []
        for a in addy:
            if '<' in a:
                continue
            if 'Store Address' in a:
                continue
                
            r_addy.append(a.strip())
            
        street_address = r_addy[0]
        city, state, zip_code = addy_ext(r_addy[1])
        
        phone_number = soup.find('p', {'class': 'PhoneNumber'}).find('a').text
        
        hours_raw = soup.find('table', {'id': 'hours_info-BS'}).prettify().split('\n')
        hours = ''
        for h in hours_raw:
            if '<' in h:
                continue
            if 'Hours of Operation:' in h:
                continue
            if 'Store Services:' in h:
                break
            
            if 'Departments:' in h:
                break
                
            hours += h.strip().replace('&amp;', '&') + ' '

        country_code = 'US'
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
