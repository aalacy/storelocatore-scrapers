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

#helper for difficult case
def addy_extractor_hard_case(src):
    arr = src.split(',')
    # special case
    if len(arr) > 2:
        city = ''
        for a in arr[:-1]:
            city += a + ' '
        city = city.strip()
    else:
        city = arr[0].strip()
    
    # deal with state and zip
    state_zip = arr[-1].split(' ')
    #normal case
    if len(state_zip) == 3:
        state = state_zip[1].strip()
        zip_code = state_zip[2].strip()
        if zip_code == '':
            zip_code = '<MISSING>'
    #probably len of 2
    else:
        state = state_zip[1].strip()
        zip_code = '<MISSING>'
    
    return city, state, zip_code 
    
def fetch_data():

    locator_domain = 'https://www.pirtekusa.com/'

    ext = 'locations/?list_by=region'
    to_scrape = locator_domain + ext

    page = session.get(to_scrape)
    assert page.status_code == 200

    soup = BeautifulSoup(page.content, 'html.parser')
    stores = soup.find_all('div', {'class': 'location_wrapper'})
    all_store_data = []

    for store in stores:
        location_name = store.find('h3').text
        
        br = store.find('p').find_all('br')
        if br[0].previousSibling.strip() == 'Mobile Service Only':
            street_address = '<MISSING>'
            location_type = 'mobile service only'
            city, state, zip_code = addy_extractor_hard_case(br[1].previousSibling)
        else:
            street_address = br[0].previousSibling.replace('\n', '').replace('\t', '')
            location_type = '<MISSING>'
            city, state, zip_code = addy_extractor(br[1].previousSibling)
            
        phone_number = br[2].previousSibling
        
        hours = '<INACCESSIBLE>'
        country_code = 'US'
        store_number = '<MISSING>'
        lat = '<MISSING>'
        longit = '<MISSING>'

        store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code,
                         store_number, phone_number, location_type, lat, longit, hours ]
        all_store_data.append(store_data)

    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
