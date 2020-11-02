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

    locator_domain = 'https://www.pioneersupermarkets.com/'

    ext = 'locations/'
    to_scrape = locator_domain + ext

    page = session.get(to_scrape)
    assert page.status_code == 200

    soup = BeautifulSoup(page.content, 'html.parser')

    stores = soup.find_all('li', {'class': 'locator-store-item'})

    all_store_data = []

    for store in stores:
        street_address = store.find('span', {'class':'locator-address'}).text
        location_name = store.find('h4', {'class':'locator-store-name'}).text
        addy_info = store.find('span', {'class':'locator-storeinformation'}).find('br').previousSibling
        city, state, zip_code = addy_extractor(addy_info)
        phone_number = store.find('a', {'class':'locator-phonenumber'}).text

        hours_html = store.find('span', {'class':'locator-storehours'})
        if hours_html == None:
            hours = '<MISSING>'
        else:
            hours = ''
            hours_split = hours_html.text.split('\n')
            for hou in hours_split:
                hours += hou + ' '
            hours = hours.strip()
            
        country_code = 'US'
        store_number = '<MISSING>'
        location_type = '<MISSING>'
        lat = '<INACCESSIBLE>'
        longit = '<INACCESSIBLE>'
        
        store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code,
                     store_number, phone_number, location_type, lat, longit, hours ]
        all_store_data.append(store_data)

    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
