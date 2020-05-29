import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import time

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def ul_extractor(ul, link_list):
    locator_domain = 'https://www.acecashexpress.com/' 

    locs = ul.find_all('p', {'class': 'location'})
    for loc in locs:
        link = loc.find('a')['href']
        link_list.append(locator_domain[:-1] + link)
    
def fetch_data():
    session = SgRequests()
    HEADERS = { 'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36' }
    locator_domain = 'https://www.acecashexpress.com/' 
    ext = 'locations'
    r = session.get(locator_domain + ext, headers = HEADERS)
    soup = BeautifulSoup(r.content, 'html.parser')

    locs = soup.find('ul', {'class': 'states'}).find_all('a')
    state_list = []
    for loc in locs:
        state_list.append(locator_domain[:-1] + loc['href'])

    city_list = []
    for state in state_list:
        r = session.get(state, headers = HEADERS)
        soup = BeautifulSoup(r.content, 'html.parser')
        cities = soup.find('ul', {'class': 'cities-list'}).find_all('a')
        for city in cities:
            city_list.append(locator_domain[:-1] + city['href'])

    link_list = []
    for city in city_list:
        try:
            r = session.get(city, headers = HEADERS)
        except:
            time.sleep(10)
            r = session.get(city, headers = HEADERS)

        soup = BeautifulSoup(r.content, 'html.parser')
        
        page_count = soup.find_all('p', {'class': 'page-count'})
        ul = soup.find('div',{'class': 'available-stores'}).find('ul', {'class': 'stores'})
        ul_extractor(ul, link_list)
        if len(page_count) == 0:
            continue
            
        else:
            total = int(page_count[0].text[-1])
            for i in range(2, total + 1):
                
                r = session.get(city + '/page/' + str(i) , headers = HEADERS)
                soup = BeautifulSoup(r.content, 'html.parser')
                ul = soup.find('div',{'class': 'available-stores'}).find('ul', {'class': 'stores'})
                ul_extractor(ul, link_list)

    all_store_data = []
    dup_tracker = set()
    for link in link_list:
        try:
            r = session.get(link, headers = HEADERS)
        except:
            time.sleep(10)
            r = session.get(link, headers = HEADERS)
        
        soup = BeautifulSoup(r.content, 'html.parser')
        
        street_address = soup.find('span', {'itemprop': 'streetAddress'}).text.strip()
    
        location_name =  soup.find('p', {'class': 'store'}).find('span', {'itemprop': 'name'}).text
        city = soup.find('span', {'itemprop': 'addressLocality'}).text
        state = soup.find('abbr', {'itemprop': 'addressRegion'}).text
        zip_code = soup.find('span', {'itemprop': 'postalCode'}).text
        
        phone_number = soup.find('a', {'itemprop': 'telephone'}).text.strip()
        if '()' in phone_number:
            phone_number = '<MISSING>'
        
        coords = soup.find('div', {'class': 'store-information'})
        lat = coords['data-latitude']
        if lat == '0':
            lat = '<MISSING>'
        longit = coords['data-longitude']
        if longit == '0':
            longit = '<MISSING>'
        store_number = coords['data-store']

        if street_address not in dup_tracker:
            dup_tracker.add(street_address)
        else:
            continue

        hours = ''
        lis = soup.find('ul', {'class': 'hours'}).find_all('li')
        for li in lis:
            hours += li.text + ' '
        
        hours = hours.strip()
        
        country_code = 'US'
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
