import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('drnkcoffee_com')



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

    locator_domain = 'https://drnkcoffee.com/' 
    ext = 'store-locations'
    r = session.get(locator_domain + ext, headers = HEADERS)

    soup = BeautifulSoup(r.content, 'html.parser')

    locs = soup.find_all('div', {'class': 'grid4-12'})

    all_store_data = []
    for loc in locs:
        location_name = loc.find('h4').text.strip()
        if 'Tempe' in location_name:
            break
        if 'Jeddah' in location_name:
            continue
        
        phone_number = loc.find('a', {'class': 'contact_call'}).text
        
        addy = loc.find('address').text.split(',')
        street_address = addy[0].strip()
        city = addy[1].strip()
        state_zip = addy[2].strip().split(' ')
        state = state_zip[0]
        zip_code = state_zip[1]
        if len(zip_code) != 5:
            zip_code = '<MISSING>'
        
        country_code = 'US'
        store_number = '<MISSING>'
        location_type = '<MISSING>'
        lat = '<MISSING>'
        longit = '<MISSING>'
        hours = '<MISSING>'
        page_url = '<MISSING>'
        
        store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code, 
                    store_number, phone_number, location_type, lat, longit, hours, page_url]

        all_store_data.append(store_data)
        logger.info(store_data)
        logger.info()

    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
