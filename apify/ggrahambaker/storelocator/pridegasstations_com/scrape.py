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

    locator_domain = 'https://pridegasstations.com' 
    ext = ''
    r = session.get(locator_domain + ext, headers = HEADERS)

    soup = BeautifulSoup(r.content, 'html.parser')

    locs = soup.find('li', {'id': 'menu-item-3324'}).find('ul').find_all('a')
    all_store_data = []
    link_list = [l['href'] for l in locs]

    for link in link_list:
        r = session.get(link, headers = HEADERS)
        soup = BeautifulSoup(r.content, 'html.parser')

        try:
            location_name = soup.find('a', {'itemprop': 'headline'}).text
        except:
            location_name = soup.find('h2', {'itemprop': 'headline'}).text
        
        info = soup.find('div', {'class': 'textwidget'}).find_all('p')
        
        hours = ''
        hours_arr = [i for i in info[0].prettify().split('\n') if '<' not in i]
        for h in hours_arr:
            hours += h.strip() + ' '
            
        hours = hours.strip()
        
        phone_number = info[1].text.replace('Phone:', '').strip()
        
        script = soup.find('script', {'class': 'av-php-sent-to-frontend'}).text.split('\n')
        for s in script:
            if "av_google_map['av_gmap_0']['marker']['0']" not in s:
                continue
            
            if 'address' in s:
                zip_code, street_address = s.split('= "')[1][:-2].split('  ')
                if street_address == '':
                    street_address = '<MISSING>'
                if zip_code == '':
                    zip_code = '<MISSING>'
                
            if 'state' in s:
                state = s.split('= "')[1][:-2]
                if state == '':
                    state = '<MISSING>'
            
            if 'city' in s:
                city = s.split('= "')[1][:-2]
                if city == '':
                    city = '<MISSING>'
            
            if 'lat' in s:
                lat = s.split('=')[1][:-1].strip()
            
            if 'long' in s:
                longit = s.split('=')[1][:-1].strip()
            
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
