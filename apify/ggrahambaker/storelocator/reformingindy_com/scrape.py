import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup

session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)

# main method
def pull_info(loc, locator_domain):
    location_name = loc.find('div', {'class': 'widgettitle'}).text
    spans = loc.find_all('span')
    
    br = spans[0].find('br')
    street_address = br.previousSibling
    addy_info = br.nextSibling.strip().split(' ')

    city = addy_info[0]
    state = addy_info[1]
    zip_code = addy_info[2]

    phone_number = spans[1].text
    country_code = 'US'
    location_type = '<MISSING>'
    store_number = '<MISSING>'
    lat = '<MISSING>'
    longit = '<MISSING>'
    hours = '<MISSING>'
    
    return [locator_domain, location_name, street_address, city, state, zip_code, country_code,
                 store_number, phone_number, location_type, lat, longit, hours ]

def fetch_data():

    locator_domain = 'https://reformingindy.com/'

    to_scrape = locator_domain
    page = session.get(to_scrape)
    assert page.status_code == 200

    soup = BeautifulSoup(page.content, 'html.parser')
    carmel = soup.find('section', {'id': 'contact_info-2'})
    fishers = soup.find('section', {'id': 'contact_info-3'})
    store_list = [carmel, fishers]

    all_store_data = []
    for store in store_list:
        all_store_data.append(pull_info(store, locator_domain))
        
    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
