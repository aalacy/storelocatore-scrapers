import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup

session = SgRequests()

def addy_ext(addy):
    address = addy.split(',')
    city = address[0]
    state_zip = address[1].strip().split(' ')
    state = state_zip[0]
    zip_code = state_zip[1]
    return city, state, zip_code

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    locator_domain = 'https://www.daliaspizza.com/'

    page = session.get(locator_domain)
    soup = BeautifulSoup(page.content, 'html.parser')
    main = soup.find('div', {'id': 'seed-csp4-description'})

    locs = main.find_all('p')
    all_store_data = []
    for loc in locs:
        cont = loc.text.split('\n')
        if len(cont) == 5:
            location_name = cont[0]
            street_address = cont[2]
            city, state, zip_code = addy_ext(cont[3])
            phone_number = cont[4]
            
            country_code = 'US'
            store_number = '<MISSING>'
            location_type = '<MISSING>'
            lat = '<MISSING>'
            longit = '<MISSING>'
            hours = '<MISSING>'
            page_url = '<MISSING>'
            
            store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code,
                    store_number, phone_number, location_type, lat, longit, hours, page_url ]
            all_store_data.append(store_data)
            
    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
