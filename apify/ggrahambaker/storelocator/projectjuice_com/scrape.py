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

    locator_domain = 'https://www.projectjuice.com/'

    ext = 'locations'

    to_scrape = locator_domain + ext
    page = session.get(to_scrape)
    assert page.status_code == 200

    soup = BeautifulSoup(page.content, 'html.parser')
    stores = soup.find_all('div', {'class': 'locations-list'})
    all_store_data = []

    ## for full location
    for store in stores:
        addy_info = store.find('div', {'class': 'location-address'}).text.split('\n')
        location_name = store.find('h2').text.strip()
        
        street_address = addy_info[1].replace(',', '').replace('\r', '').strip()
        
        addy_ect = addy_info[2].replace('\r', '').strip()
        
        city, state, zip_code = addy_extractor(addy_ect)
        
        phone_number = store.find('div', {'class': 'location-phone'}).text.strip()
        
        h_arr = store.find('div', {'class': 'location-hours'}).text.split('\n')
        hours = ''
        for h in h_arr:
            hours += h + ' '
        
        hours = hours.replace('   ', '').strip()
        
        country_code = 'US'
        location_type = 'location'
        store_number = '<MISSING>'
        lat = '<MISSING>'
        longit = '<MISSING>'
        
        store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code,
                     store_number, phone_number, location_type, lat, longit, hours ]
        
        all_store_data.append(store_data)

    stores = soup.find('div', {'class': 'partner-locations'})
    cols = stores.find_all('div', {'class': 'col'})
    
    ## partner locations
    for col in cols:
        location_name = col.find('h2').text.strip()
        addy_info = col.find('div', {'class': 'location-address'}).text.split('\n')
        
        street_address = addy_info[1].replace(',', '').replace('\r', '').strip()
        
        addy_ect = addy_info[2].replace('\r', '').strip()
        
        city, state, zip_code = addy_extractor(addy_ect)
        
        phone_number = col.find('div', {'class': 'location-phone'})#.text.strip()
        if phone_number == None:
            phone_number = '<MISSING>'
        else:
            phone_number = phone_number.text.strip()
            if not phone_number[-1].isdigit():
                phone_number = '<MISSING>'
        
        h_arr = col.find('div', {'class': 'location-hours'})
        
        if h_arr == None:
            
            hours = '<MISSING>'
        else:
            h_arr = h_arr.text.split('\n')
            hours = ''
            for h in h_arr:
                hours += h + ' '
            
            hours = hours.replace('   ', '').strip()
            
        country_code = 'US'
        location_type = 'partner location'
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
