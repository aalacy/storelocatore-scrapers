import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('californiaparking_com')



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

    locator_domain = 'https://californiaparking.com/' 
    ext = 'san-francisco-parking-locations.shtml'
    r = session.get(locator_domain + ext, headers = HEADERS)

    soup = BeautifulSoup(r.content, 'html.parser')

    locs = soup.find_all('a', {'class': ['btn', 'btn-primary', 'btn-inversed', 'btn-small']})

    link_list = []
    for loc in locs:
        link_list.append(loc['href'])

    all_store_data = []
    for link in link_list:
        logger.info(locator_domain + link)
        logger.info()
        r = session.get(locator_domain + link, headers = HEADERS)
        soup = BeautifulSoup(r.content, 'html.parser')
        location_name = soup.find('h2').text.split(',')[0]
        street_address = location_name
    
        google_href = soup.find('iframe')['src']
        
        start = google_href.find('!2d')
        end = google_href.find('!2m')
        coords = google_href[start + 3: end].split('!3d')

        longit = coords[0]
        lat = coords[1]
        if '!3m' in lat:
            lat = lat.split('!3m')[0]
        
        boxes = soup.find_all('div', {'class': 'box'})
        for b in boxes:
            if 'Monday' in b.text:
                if 'Rate' in b.text:
                    continue
        
                hours = ' '.join(b.text.replace('\n', ' ').strip().split())
                hours = hours.split('*')[0]
                        
        city = '<MISSING>'
        state = '<MISSING>'
        zip_code = '<MISSING>'
        country_code = 'US'
        store_number = '<MISSING>'
        phone_number = '<MISSING>'
        location_type = '<MISSING>'
        page_url = locator_domain + link
        store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code, 
                    store_number, phone_number, location_type, lat, longit, hours, page_url]

        all_store_data.append(store_data)

    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
