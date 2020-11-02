import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup

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

    locator_domain = 'https://www.muchoburritous.com/' 
    ext = 'locator/index.php?brand=35&mode=desktop&pagesize=5&latitude=&longitude=&q=20001'
    r = session.get(locator_domain + ext, headers = HEADERS)

    soup = BeautifulSoup(r.content, 'html.parser')

    stores = soup.find('div', {'class': 'storelist'}).find_all('div', {'class': 'inner'})

    all_store_data = []

    for store in stores:
        location_name = store.find('h2').text
        store_number = location_name.split('#')[1]
        street_address = store.find('p', {'class': 'full-address'}).text
        addy_ext = store.find('p', {'class': 'list-address'}).find_all('span')
        city = addy_ext[0].text.replace(',', '').strip()
        state = addy_ext[1].text
        zip_code = addy_ext[2].text
        
        phone_number = store.find('p', {'class': 'phone'}).text
        
        buttons = store.find('div', {'class': 'buttons'}).find_all('a')
        page_url = locator_domain[:-1] + buttons[-1]['href']    
        
        r = session.get(page_url, headers = HEADERS)
        soup = BeautifulSoup(r.content, 'html.parser')
        
        hours = ''
        for li_item in soup.find_all('li'):
            if 'PM' in li_item.text:
                hours += li_item.text + ' '
                
        if hours == '':
            hours = '<MISSING>'
            
        country_code = 'US'
        
        location_type = '<MISSING>'
        lat = '<MISSING>'
        longit  = '<MISSING>'
        
        store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code, 
                    store_number, phone_number, location_type, lat, longit, hours, page_url]

        all_store_data.append(store_data)

    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
