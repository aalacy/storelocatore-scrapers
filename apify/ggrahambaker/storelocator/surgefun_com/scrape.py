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

def addy_ext(addy):
    com_split = addy.split(',')
    city = com_split[0]
    state_zip = com_split[1].strip().split(' ')
    state = state_zip[0]
    zip_code = state_zip[1]
    
    return city, state, zip_code

def fetch_data():
    session = SgRequests()
    HEADERS = { 'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36' }

    locator_domain = 'https://surgefun.com'

    response = session.get(locator_domain, headers = HEADERS)
    soup = BeautifulSoup(response.content, 'html.parser')
    locs = soup.find_all('div', {'class': 'side-nav-link'})

    link_list = []
    for loc in locs:
        link = loc.find('a')['href']
        link_list.append(locator_domain + link)
        
    all_store_data = []
    for link in link_list:
        
        response = session.get(link + '/ContactUs/', headers = HEADERS)
        soup = BeautifulSoup(response.content, 'html.parser')
        # print(link)
        location_name = soup.find('span', {'id': 'header-location'}).text.strip()
        
        google_link = soup.find('div', {'class': 'google-map'}).find('iframe')['src']
        start = google_link.find('!2d')
        end = google_link.find('!2m')
        
        coords = google_link[start + 3 : end].split('!3d')
        lat = coords[1]
        longit = coords[0]
        
        conts = soup.find_all('div', {'class': 'footer-address'})

        for i, c in enumerate(conts):
            if i == 0:
                addy = c.text.strip().split('\n')
                street_address = addy[0].strip()
                city, state, zip_code = addy_ext(addy[1].strip())
                
            elif i == 1:
                phone_number = c.text.strip()

            else:
                continue

        if "@" in phone_number:
            phone_number = '<MISSING>'
            
        days = soup.find_all('div', {'class': 'Footer-Hours'})
        
        hours = ''
        for d in days:
            day = ' '.join(d.text.strip().split())

            hours += day

        hours = hours.replace("PM","PM ").replace("Closed","Closed ").strip()
        if not hours:
            hours = '<MISSING>'
        
        country_code = '<MISSING>'
        store_number = '<MISSING>'
        location_type = '<MISSING>'
        page_url = link
        
        store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code, 
                    store_number, phone_number, location_type, lat, longit, hours, page_url]
        all_store_data.append(store_data)

    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
