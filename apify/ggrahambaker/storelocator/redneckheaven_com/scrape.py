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

#helper for getting address
def addy_extractor(src):
    arr = src.split(',')
    city = arr[0]
    prov_zip = arr[1].split(' ')
    if len(prov_zip) == 3:
        state = prov_zip[1]
        zip_code = prov_zip[2]
    
    return city, state, zip_code

def fetch_data():
    locator_domain = 'http://redneckheaven.com/'
    ext = 'redneck-location/'

    to_scrape = locator_domain + ext
    page = session.get(to_scrape)
    assert page.status_code == 200
    
    soup = BeautifulSoup(page.content, 'html.parser')
    stores = soup.find_all('div', {'class': 'rh__feature__location'})
    all_store_data = []

    for store in stores:
        brs = store.find('p', {'class': 'rh__feature--paragraph text-center'}).find_all('br')

        street_address = brs[0].previousSibling.strip()
        city, state, zip_code = addy_extractor(brs[2].previousSibling.strip())

        a_tags = store.find_all('a')
        location_name = a_tags[0].text

        phone_number = a_tags[1].text.strip()

        country_code = 'US'
        location_type = '<MISSING>'
        store_number = '<MISSING>'
        lat = '<MISSING>'
        longit = '<MISSING>'
        hours = '<MISSING>'
        
        store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code,
                     store_number, phone_number, location_type, lat, longit, hours ]
        all_store_data.append(store_data)
        
    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
