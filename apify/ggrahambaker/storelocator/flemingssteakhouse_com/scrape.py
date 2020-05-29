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

    locator_domain = 'https://www.flemingssteakhouse.com/' 
    ext = 'locations'
    r = session.get(locator_domain + ext, headers = HEADERS)

    soup = BeautifulSoup(r.content, 'html.parser')

    states = soup.find_all('ul', {'class': 'locations'})
    link_list = []
    for s in states:
        links = s.find_all('a')
        for l in links:
            link_list.append(l['href'])

    all_store_data = []
    for link in link_list:
        if 'coming-soon' in link:
            continue
        r = session.get(link, headers = HEADERS)

        soup = BeautifulSoup(r.content, 'html.parser')
        main = soup.find('div', {'class': 'col-lg-4'})
        cont = []
        for element in main.prettify().split('\n'):
            if '<' not in element:
                cont.append(element.strip())

        location_name = soup.find('h1').text
        
        street_address = cont[1]
        city, state, zip_code = addy_ext(cont[2])
        
        phone_number = cont[3]

        hours = cont[7]
        if 'Local' in hours:
            hours = cont[6]
        
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
