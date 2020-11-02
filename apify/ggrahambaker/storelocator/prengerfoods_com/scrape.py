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

## helper to catch duplicates
def validator(all_store_data):
    addresses = []
    all_store_data_clean = []
    for data in all_store_data:
        if data[2] not in addresses:
            all_store_data_clean.append(data)
            addresses.append(data[2])
    return all_store_data_clean
            
def fetch_data():
    locator_domain = 'https://prengerfoods.com/'
    ext = 'Home/Locations'
    to_scrape = locator_domain + ext
    page = session.get(to_scrape)
    assert page.status_code == 200
    soup = BeautifulSoup(page.content, 'html.parser')
    stores = soup.find_all('p', class_='contact_details') 

    all_store_data = []
    ## there are duplicates on bottom of page
    for store in stores[:8]:
        store_pretty = store.prettify()
        
        items = store_pretty.split('<br')
        loc_name_cut = items[0].split('<b>')[1].index('<')
        location_name = items[0].split('<b>')[1][:loc_name_cut].strip()
        
        st_addy_cut = items[1].index('>') + 1
        street_address = items[1][st_addy_cut:].strip()
        
        addy_info_cut = items[2].index('>') + 1
        addy_info_clean = items[2][addy_info_cut:].strip()
        addy_info_arr = addy_info_clean.split(' ')
        
        if len(addy_info_arr) == 4:
            # spaces in addy
            city_idx = 0
            state_idx = 2
            zip_idx = 3
        else:
            city_idx = 0
            state_idx = 1
            zip_idx = 2
            
        if ',' in addy_info_arr[city_idx]:
            # gotta strip
            city = addy_info_arr[city_idx].strip()[:-1]
        else:
            city = addy_info_arr[city_idx].strip()
            
        state = addy_info_arr[state_idx].strip()
        zip_code = addy_info_arr[zip_idx].strip()
        
        country_code = 'US'
        store_number = '<MISSING>'
        
        phone_cut = items[3].index('>') + 1
        phone_number = items[3][phone_cut:].strip()
        
        location_type = '<MISSING>'
        lat = store.findNext('div')['data-lat']
        longit = store.findNext('div')['data-lng'] 
    
        ## check for 'style', they will be in 4!
        if 'style' in items[4]:
            hours = items[4].split('</b>')[1].strip()
        else:
            hours = items[5].split('</b>')[1].split('</p>')[0].strip()
            
        # done parsing, lets push it to an array
        # should be like this
        # locator_domain, location_name, street_address, city, state, zip, country_code,
        # store_number, phone, location_type, latitude, longitude, hours_of_operation
        store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code,
                     store_number, phone_number, location_type, lat, longit, hours ]
        all_store_data.append(store_data)
    
    return validator(all_store_data)

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
