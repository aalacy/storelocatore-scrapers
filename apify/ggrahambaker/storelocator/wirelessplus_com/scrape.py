import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import json

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

    locator_domain = 'https://www.wirelessplus.com' 
    ext = '/locations/'

    r = session.get(locator_domain + ext, headers = HEADERS)
    soup = BeautifulSoup(r.content, 'html.parser')

    all_ul = soup.find_all('ul', {'class': 'location-store-list'})
    all_store_data = []
    for ul in all_ul:
        lis = ul.find_all('li')
        for li in lis:
            link = li.find('a')['href']
            
            page_url = locator_domain + link
            print(page_url)
            r = session.get(page_url, headers = HEADERS)
            soup = BeautifulSoup(r.content, 'html.parser')
            
            loc_info = soup.find_all('script', {'type': 'application/ld+json'})
            for script in loc_info:
                loc_json = json.loads(script.text)

                if loc_json['@type'] == 'BreadcrumbList':
                    continue
                    
                strongs = soup.find_all('strong')
                hours = ''
                for st in strongs:
                    
                    if 'Store hours:' in st.text:
                        hour_info = st.parent.find('div', {'class': 'row'}).find_all('div')
                        for info in hour_info:
                            hours += info.text.strip()
                        
                hours = hours.replace("day","day ").replace("pm","pm ").replace("Closed","Closed ").strip()   
                location_name = loc_json['name']
                if 'telephone' in loc_json:
                    phone_number = loc_json['telephone']
                else:
                    phone_number = '<MISSING>'

                addy = loc_json['address']

                street_address = addy['streetAddress']
                city = addy['addressLocality']
                state = addy['addressRegion']
                zip_code = addy['postalCode']
                country_code = 'US'

                try:
                    coords = loc_json['geo']
                    lat = coords['latitude']
                    longit = coords['longitude']
                except:
                    lat = '<MISSING>'
                    longit = '<MISSING>'                    

                store_number = page_url.split("/")[-3]
                location_type = '<MISSING>'

                store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code, 
                            store_number, phone_number, location_type, lat, longit, hours, page_url]

                all_store_data.append(store_data)

    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
