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

# helper for addy
def addy_extractor(src):
    arr = src.split(',')
    if len(arr) == 3:
        city = arr[0].strip()
        state = arr[1].strip()
        zip_code = arr[2].strip()
    else:
        city = arr[0].strip()
        prov_zip = arr[1].split(' ')
        if len(prov_zip) == 3:
            state = prov_zip[1].strip()
            zip_code = prov_zip[2].strip()
    
    return city, state, zip_code

def fetch_data():
    locator_domain = 'https://www.reids.com/'
    ext = 'locations'

    to_scrape = locator_domain + ext
    page = session.get(to_scrape)
    assert page.status_code == 200
    
    soup = BeautifulSoup(page.content, 'html.parser')
    stores = soup.find_all('div', {'class': 'row'})
    all_store_data = []
    
    content_i = [1, 3, 5, 7]
    div = stores[3].find_all('div', {'class':'col-xs-12 col-sm-6'})

    for i in content_i:
        store = div[i]
        location_name = store.find('h3').text.strip()
        
        ps = store.find_all('p')
        br = ps[0].find('br')
        street_address = br.previousSibling
        city, state, zip_code = addy_extractor(br.nextSibling.strip())
        
        phone_number = ps[1].text.replace('Store Phone: ', '').strip()
        br_h = ps[2].find_all('br')
        hours = ''
        if i < 4 or i > 6:
            hours = br_h[0].nextSibling.strip() + ' ' + br_h[1].nextSibling.strip()
        else:
            hours = br_h[0].nextSibling.strip() + ' '+ ps[3].text
            
        if ' Director' in hours:
            hours = hours.split(' Director')[0]
        
        country_code = 'US'
        location_type = '<MISSING>'
        store_number = '<MISSING>'
        lat = '<MISSING>'
        longit = '<MISSING>'
        if ':' in phone_number:
            phone_number = phone_number.split(':')[1].strip()
        
        store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code,
                     store_number, phone_number, location_type, lat, longit, hours ]
        all_store_data.append(store_data)

    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
