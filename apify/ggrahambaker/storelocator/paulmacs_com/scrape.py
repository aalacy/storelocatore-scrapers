import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re

session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)

# helper
def coord_extractor(src):
    split = src.split('/')
    coords = split[-1].split('-')
    lat = coords[0]
    longit = '-' + coords[1].replace('.png', '')
    return([lat, longit])
  
## helpter  
def addy_extractor(src):
    arr = src.split(',')
    city = arr[0]
    prov_zip = arr[1].split(' ')
    if len(prov_zip) == 3:
        state = prov_zip[1]
        zip_code = prov_zip[2][0:3] + ' ' + prov_zip[2][3:]
    else:
        state = prov_zip[1]
        zip_code = prov_zip[2] + ' ' + prov_zip[3]
    
    return [city, state, zip_code]

def fetch_data():
    locator_domain = 'http://paulmacs.com/' 
    ext = 'store-locator'

    to_scrape = locator_domain + ext
    page = session.get(to_scrape)
    assert page.status_code == 200

    soup = BeautifulSoup(page.content, 'html.parser')
    stores = soup.find('div', {'id': 'list_view'})
    lis = stores.find_all('li')

    all_store_data = []

    for li in lis[:-4]:
        location_name = li.find('span', {'class': 'h1'}).text
        
        #print(li.find('p', {'class': 'address'}).text.strip().replace('\t', '').split('\n'))
        addy_info = li.find('p', {'class': 'address'}).text.strip().replace('\t', '').split('\n')
        
        if len(addy_info) == 2:
            street_address = addy_info[0]
            addy_info = addy_extractor(addy_info[1])
            city = addy_info[0]
            state = addy_info[1]
            zip_code = addy_info[2]
        else:
            street_address = addy_info[0] + ' ' + addy_info[1]
            addy_info = addy_extractor(addy_info[2])
            city = addy_info[0]
            state = addy_info[1]
            zip_code = addy_info[2]
            
        #print(li.find_all('p', {'class': 'days'}))
        h = li.find_all('p', {'class': 'days'})
        hours = ''
        for ho in h:
            hours += ho.text + ' '
            hours += ho.nextSibling.text + ' '
        hours = hours.strip()
        coords = coord_extractor(li.find('img')['src'])
        lat = coords[0]
        longit = coords[1]
        country_code = 'CA'
        phone_number = li.find('p', {'class': 'address'}).nextSibling.text.strip().replace('Phone: ', '')
        location_type = '<MISSING>'
        store_number = '<MISSING>'
        
        store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code,
                     store_number, phone_number, location_type, lat, longit, hours ]
        all_store_data.append(store_data)

    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
