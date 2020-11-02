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

    locator_domain = 'http://www.expressparking.us/'
    ext = 'locations'

    response = session.get(locator_domain + ext, headers = HEADERS)
    soup = BeautifulSoup(response.content, 'html.parser')

    locs = soup.find_all('div', {'class': 'LocationRow'})
    all_store_data = []
    for loc in locs:
        location_name = loc.find('h3').text
        if 'Corporate' in location_name:
            location_type = 'Corporate Office'
        else:
            location_type = '<MISSING>'
        store_number = location_name.strip()[-1:]
        ps = loc.find('div', {'class': 'Address'}).find_all('p')
        
        addy_phone = ps[0]
        info = str(addy_phone).split('<br/>')

        street_address = info[0].replace('<p>', '')
        city, state, zip_code = addy_ext(info[1])

        if len(info) == 3:
            phone_number = info[2].replace('Tel:', '').replace('</p>', '').strip()

        else:
            zip_code = zip_code.replace('</p>', '')
            phone_number = '<MISSING>'
      
        if len(ps) == 1:
            hours = '<MISSING>'
        else:
            hours_html = ps[1]
            hours_arr = str(hours_html).replace('<p>', '').replace('</p>', '').strip().split('<br/>')
            hours = ''
            for h in hours_arr:
                hours += h + ' '
                
            hours = hours.strip()

        google_href = loc.find_all('iframe')
        if len(google_href) == 1:
            
            google_href = google_href[0]['src']
            start = google_href.find('!2d')
            end = google_href.find('!2m')
            coords = google_href[start + 3: end].split('!3d')

            longit = coords[0]
            lat = coords[1]
        else:
            lat = '<MISSING>'
            longit = '<MISSING>'
        
        country_code = 'US'
        page_url = '<MISSING>'
        store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code, 	
                    store_number, phone_number, location_type, lat, longit, hours, page_url]
        all_store_data.append(store_data)
        
    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
