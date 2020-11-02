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

def fetch_data():
    session = SgRequests()
    HEADERS = { 'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36' }

    locator_domain = 'https://www.westsidepizza.com/' 
    ext = 'locations/'
    r = session.get(locator_domain + ext, headers = HEADERS)

    soup = BeautifulSoup(r.content, 'html.parser')

    locs = soup.find('div', {'id': 'block-narwhal-content'}).find_all('div', {'class': 'views-row'})

    all_store_data = []
    for loc in locs:
        page_url = locator_domain[:-1] + loc.find('div', {'class': 'views-field-view-node'}).find('a')['href']
        r = session.get(page_url, headers = HEADERS)
        soup = BeautifulSoup(r.content, 'html.parser')

        strongs = soup.find_all('strong')
        hours = ''
        for s in strongs:
            if 'Store Hours' in s.text:
                hours_ps = s.parent.parent.find_all('p')
                for h in hours_ps[1:]:
                    hours += ' '.join(h.text.split()) + ' '
        
        hours = hours.strip()        
        street_address = soup.find('div', {'class': 'field-address'}).text
        city = soup.find('div', {'class': 'field-city'}).text
        state = soup.find('div', {'class': 'field-state'}).text
        zip_code = soup.find('div', {'class': 'field-zip-code'}).text

        location_name = soup.find('h1', {'class': 'title'}).text.strip()

        phone_number = soup.find('div', {'class': 'field-phone'}).text

        store_number = '<MISSING>'
        location_type = '<MISSING>'
        country_code = 'US'
        lat = '<MISSING>'
        longit = '<MISSING>'
        
        store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code, 
                    store_number, phone_number, location_type, lat, longit, hours, page_url]
        all_store_data.append(store_data)

    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
