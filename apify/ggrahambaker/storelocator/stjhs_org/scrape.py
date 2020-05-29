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

    locator_domain = 'https://www.saintlukeshealthsystem.org/' 
    ext = 'our-locations/'
    r = session.get(locator_domain + ext, headers = HEADERS)
    soup = BeautifulSoup(r.content, 'html.parser')
    regions = soup.find('ul', {'class': 'slide-list'}).find_all('li', {'class': 'level1'})

    links = [locator_domain[:-1] + reg.find('a')['href'] for reg in regions]

    link_list = []
    for link in links:
        r = session.get(link, headers = HEADERS)
        soup = BeautifulSoup(r.content, 'html.parser')
        
        hrefs = soup.find_all('a', {'class': 'btn'})
        for h in hrefs:
            link_list.append(locator_domain[:-1] + h['href'])

    all_store_data = []
    for link in link_list:
        r = session.get(link, headers = HEADERS)
        soup = BeautifulSoup(r.content, 'html.parser')

        location_name = soup.find('h1', {'itemprop': 'name'})
        if location_name == None:
            continue
        else:
            location_name = location_name.text
        street_address = soup.find('span', {'itemprop': 'streetAddress'}).text.split(',')[0]

        city = soup.find('span', {'itemprop': 'addressLocality'})
        
        if city == None:
            continue
        else:
            city = city.text.replace(',', '')
            
        state = soup.find('span', {'itemprop': 'addressRegion'}).text
        
        zip_code = soup.find('span', {'itemprop': 'postalCode'}).text
        page_url = soup.find('a', {'class': 'v5'})['href']
        
        phone_number = soup.find('a', {'class': 'phone'}).text
        
        country_code = 'US'
        store_number = '<MISSING>'
        lat = '<MISSING>'
        longit = '<MISSING>'
        hours = '<MISSING>'
        location_type = '<MISSING>'
        store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code, 
                    store_number, phone_number, location_type, lat, longit, hours, page_url]

        all_store_data.append(store_data)
        
    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
