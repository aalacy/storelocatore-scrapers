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
    addy = addy.split(',')
    city = addy[0]
    state_zip = addy[1].strip().split(' ')
    state = state_zip[0]
    zip_code = state_zip[1]
    return city, state, zip_code

def fetch_data():
    session = SgRequests()
    HEADERS = { 'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36' }

    locator_domain = 'https://www.greggsusa.com'
    ext = '/Locations'
    response = session.get(locator_domain + ext, headers = HEADERS)

    soup = BeautifulSoup(response.content, 'html.parser')
    loc_lists = soup.find_all('div', {'class': 'locationlist'})
    link_list = []
    for loc_l in loc_lists:
        
        pics = loc_l.find_all('div', {'class': 'imagedivleft'})
        for pic in pics:
            tag = pic.find('a')
            
            link_list.append(tag['href'])

    all_store_data = []
    for link in link_list:
        response = session.get(locator_domain + link, headers = HEADERS)
        soup = BeautifulSoup(response.content, 'html.parser')
        addy = soup.find('div', {'class': 'locationaddress'}).find('p').text.replace('\r','').split('\n')
        street_address = addy[0].strip()
        city, state, zip_code = addy_ext(addy[1].strip())
        
        phone_number = addy[2].strip()
        
        hours_ps = soup.find('div', {'class': 'hours'}).find_all('p')
        hours = ''
        for h in hours_ps:
            d = h.find('span').text
            t = h.text.replace(d, '').strip()
            hours += d + ' ' + t + ' '
        
        hours = hours.strip()
        
        google_href = soup.find('div', {'class': 'map-container'}).find('iframe')['src']
        
        start = google_href.find('!2d')
        end = google_href.find('!2m')
        coords = google_href[start + 3: end].split('!3d')

        longit = coords[0]
        lat = coords[1]
        
        location_name = soup.find('div', {'class': 'location'}).find('h2').text

        country_code = 'US'
        store_number = '<MISSING>'
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
