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

    locator_domain = 'https://www.pbteen.com/' 
    url = 'https://www.potterybarnkids.com/customer-service/store-locator.html'

    r = session.get(url, headers = HEADERS)
    soup = BeautifulSoup(r.content, 'html.parser')

    locs = soup.find('section', {'id': 'united-states'}).find_all('div', {'class': 'store-card'})
    link_list = []
    for l in locs:
        link_list.append(l.find('a')['href'])

        
    locs = soup.find('section', {'id': 'canada'}).find_all('div', {'class': 'store-card'})
    for l in locs:
        link_list.append(l.find('a')['href'])



    all_store_data = []
    for link in link_list:
        r = session.get(link, headers = HEADERS)
        page_url = link
        hours = ''
        pushing_on = False
        
        lat = ''
        longit = ''
        zip_code = ''
        
        for i, line in enumerate(r.content.decode().splitlines()):
            
            if line.strip().startswith("lat:'"):
                lat = line.strip().replace('lat:', '').replace("'", '').replace(',', '')
            
            if line.strip().startswith("lng:'"):
                longit = line.strip().replace('lng:', '').replace("'", '').replace(',', '')
            
            if line.strip().startswith('zipCode:'):
                zip_code = line.strip().replace('zipCode:', '').replace("'", '').replace(',', '')
            
            
            if line.strip().startswith("origin:{"):
                break
            
                
            if pushing_on:
                start = line.strip().find('day:')
                end = line.strip().find("',")
                day = line.strip()[start + 6: end]
                start = line.strip().find('hours:')
                end = line.strip().find("'}")
                h = line.strip()[start + 8: end]
                
                
                hours += day + ' ' + h + ' '
            
            if line.strip().startswith("storeHours:["):
            
                pushing_on = True
                
                
        hours = hours.strip()
        soup = BeautifulSoup(r.content, 'html.parser')
        location_name = soup.find('h3', {'itemprop': 'name'}).text
        street_address = soup.find('p', {'class': 'storeDetailsAddress'}).text.strip()
        city = soup.find('span', {'itemprop': 'addressLocality'}).text
        state = soup.find('span', {'itemprop': 'addressRegion'}).text
        
        
        if '/ca/' in page_url:
            country_code = 'CA'
        
        if '/us/' in page_url:
            country_code = 'US'
        
        phone_number = soup.find('p', {'itemprop': 'telephone'}).text
        
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
