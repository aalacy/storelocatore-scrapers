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

    locator_domain = 'http://www.schnippers.com/' 

    r = session.get(locator_domain, headers = HEADERS)
    soup = BeautifulSoup(r.content, 'html.parser')

    locs = soup.find('div', {'id': 'restaurant-list'}).find_all('li', {'class' : 'restaurant'})
    loc_list = [] 
    for loc in locs:
        link = loc.find('a', {'class': 'location'})['href']
        loc_list.append(link)

    all_store_data = []
    for url in loc_list:
        page_url = url
        r = session.get(url, headers = HEADERS)

        soup = BeautifulSoup(r.content, 'html.parser')

        location_name = soup.find('div', {'class': 'location-neighborhood'}).text
        phone_number = soup.find('a', {'class': 'telephone'}).text.replace('Call', '').strip()
        
        street_address = soup.find('h1', {'class': 'location-number'}).text.split('Call')[0]
        
        hours_div = soup.find('div', {'class': 'col1'})
        
        is_hours = hours_div.find('h2')
        if 'Hours' in is_hours.text:
            hours = is_hours.findNext('p').text
        
        google_src = soup.find('div', {'class': 'col2'}).find('iframe')['src']
        
        start = google_src.find('!2d')
        end = google_src.find('!3m')
        
        coords = google_src[start + 3 : end].split('!3d')
        
        lat = coords[1].split('!')[0]
        longit = coords[0]
        
        city = '<MISSING>'
        state = '<MISSING>'
        zip_code = '<MISSING>'
        country_code = 'US'
        store_number = '<MISSING>'
        location_type = '<MISSING>'
        
        store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code, 
                    store_number, phone_number, location_type, lat, longit, hours, page_url]

        all_store_data.append(store_data)

    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
