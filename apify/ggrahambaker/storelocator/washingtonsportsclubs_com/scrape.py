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

    locator_domain = 'https://www.washingtonsportsclubs.com/' 
    ext = 'clubs'
    r = session.get(locator_domain + ext, headers = HEADERS)
    soup = BeautifulSoup(r.content, 'html.parser')

    locs = soup.find_all('li', {'class': 'club-tile'})

    link_list = []
    for loc in locs:
        link = locator_domain[:-1] + loc.find('a')['href']
        
        if link not in link_list:
            link_list.append(link)

    all_store_data = []
    for link in link_list:
        r = session.get(link, headers = HEADERS)
        soup = BeautifulSoup(r.content, 'html.parser')
        
        location_name = soup.find('h1', {'itemprop': 'name'}).text.strip()
        street_address = soup.find('span', {'itemprop': 'streetAddress'}).text.strip()
        city = soup.find('span', {'itemprop': 'addressLocality'}).text.strip()
        state = soup.find('span', {'itemprop': 'addressRegion'}).text.strip()
        if state == '':
            state = '<MISSING>'

        zip_code = soup.find('span', {'itemprop': 'postalCode'}).text.strip()

        phone_number = soup.find('span', {'itemprop': 'telephone'}).text.strip()

        hour_spans = soup.find_all('span', {'itemprop': 'openingHours'})
        hours = ''
        for h in hour_spans:
            hours += h['content'].strip() + ' '
            
        country_code = 'US'
        store_number = '<MISSING>'
        location_type = '<MISSING>'
        lat = '<MISSING>'
        longit = '<MISSING>'
        page_url = link
        store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code, 
                    store_number, phone_number, location_type, lat, longit, hours, page_url]

        all_store_data.append(store_data)
            
    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
