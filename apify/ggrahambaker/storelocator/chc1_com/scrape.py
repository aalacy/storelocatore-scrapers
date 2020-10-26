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

    locator_domain = 'https://www.chc1.com/' 
    ext = 'locations/'
    r = session.get(locator_domain + ext, headers = HEADERS)

    soup = BeautifulSoup(r.content, 'html.parser')
    locs = soup.find('div', {'id': 'chclocations'}).find_all('div', {'class': 'col-6'})
    link_list = []
    for loc in locs:
        link = loc.find('a')['href']
        link_list.append(link)
        
    all_store_data = []
    for link in link_list:
        print(link)
        r = session.get(link, headers = HEADERS)
        soup = BeautifulSoup(r.content, 'html.parser')
        info = soup.find('div', {'class': 'col-sm-5'})
        
        location_name = info.find('strong').text

        addy_phone = info.find_all('p')
        addy = [a.strip() for a in addy_phone[0].prettify().split('\n') if '>' not in a]

        street_address = addy[0]
        if len(addy) > 3:
            city, state, zip_code = addy_ext(addy[2])
        else:
            city, state, zip_code = addy_ext(addy[1])

        phone_number = [a.strip() for a in addy_phone[1].prettify().split('\n') if '>' not in a][0]
        
        map_hours = soup.find('div', {'class': 'col-sm-7'})
        
        google_link = map_hours.find('iframe')['src']

        start = google_link.find('!2d')
        end = google_link.find('!2m')
        coords = google_link[start + 3: end].split('!3d')
        lat = coords[1].split('!3m')[0]
        longit = coords[0]
        
        hours_split = map_hours.find('tbody').prettify().split('\n')

        dont_eat = False
        hours = ''
        for h in hours_split:
            if '<del>' in h:
                dont_eat = True
            if '</del>' in h:
                dont_eat = False
                
            if '<' in h:
                continue
            
            if dont_eat:
                continue
                
            if 'Closed' in h:
                continue
            hours += h.strip() + ' '
        
        country_code = 'US'
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
