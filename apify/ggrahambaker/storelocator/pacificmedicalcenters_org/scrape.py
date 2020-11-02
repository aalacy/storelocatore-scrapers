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
    if len(addy) == 1:
        addy = addy[0].split(' ')
        city = addy[0]
        state = addy[1]
        zip_code = addy[2]
    else:
        city = addy[0]
        state_zip = addy[1].strip().split(' ')
        state = state_zip[0]
        zip_code = state_zip[1]
    return city, state, zip_code

def fetch_data():
    session = SgRequests()
    HEADERS = { 'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36' }

    locator_domain = 'https://www.pacificmedicalcenters.org/' 
    ext = 'where-we-are/'

    r = session.get(locator_domain + ext, headers = HEADERS)

    soup = BeautifulSoup(r.content, 'html.parser')

    menu = soup.find('div', {'id': 'mapLocations'})

    locs = menu.find_all('h5')
    all_store_data = []
    for loc in locs:
        link_name = loc.find('span').find('a')#['href']
       
        page_url = locator_domain[:-1] + link_name['href']
        r = session.get(page_url, headers = HEADERS)

        soup = BeautifulSoup(r.content, 'html.parser')
        
        location_name = soup.find('h3').text
        addy_raw = soup.find('p', {'id': 'address'}).prettify().split('\n')
        addy_raw2 = [a for a in addy_raw if '<' not in a]
        addy = []
        loc_moved = False
        for a in addy_raw2:
            if "COVID" in a:
                loc_moved = True
            if a == '':
                continue
            
            addy.append(a.strip())
        
        if loc_moved:
            loc_moved = False
            continue
            
        if len(addy) == 3:
            addy = [addy[0], addy[2]]

        street_address = addy[0].strip().split(',')[0]
        city, state, zip_code = addy_ext(addy[1].strip())
        
        frames = soup.find_all('iframe')
        for f in frames:
            if '/maps/' in f['src']:
                google_link = f['src']

        start = google_link.find('!2d')
        end = google_link.find('!2m')
        coords = google_link[start + 3: end].split('!3d')

        longit = coords[1]
        lat = coords[0]

        country_code = 'US'
        store_number = '<MISSING>'
        location_type = '<MISSING>'
        
        hours = '<MISSING>'
        phone_number = '<MISSING>'
             
        store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code, 
                    store_number, phone_number, location_type, lat, longit, hours, page_url]

        all_store_data.append(store_data)

    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
