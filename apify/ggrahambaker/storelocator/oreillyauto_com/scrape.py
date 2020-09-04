import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import sgzip 
import json
import time

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

    search = sgzip.ClosestNSearch()
    search.initialize()

    coord = search.next_coord()
    link_list = []
    all_store_data = []
    locator_domain = 'https://www.oreillyauto.com/'
    while coord:
        coords = []

        #print('------------------------')
        #print("remaining zipcodes: " + str(search.zipcodes_remaining()))
        x = coord[0]
        y = coord[1]

        #print('Pulling Lat-Long %s,%s...' % (str(x), str(y)))
        url = 'https://www.oreillyauto.com/stores/list?lat=' + str(x) + '&lng=' + str(y)
        #print(url)
        try:
            r = session.get(url, headers=HEADERS)
        except:
            #print('sleeeeeping \n\n\n\n\n\n\n')
            time.sleep(15)
            r = session.get(url, headers=HEADERS)
            #print(':)')
        soup = BeautifulSoup(r.content, 'html.parser')
        coords.append((x, y))
 
        hrefs = soup.find_all('a', {'class': 'js-fas-details-link'})
        
        for h in hrefs:
            link = h['href']
            if link not in link_list:
                
                link_list.append(link)
                
                r = session.get(link, headers=HEADERS)
                soup = BeautifulSoup(r.content, 'html.parser')
                page_url = link

                loc_jsons = soup.find_all('script', {'type': 'application/ld+json'})
                
                if len(loc_jsons) > 1:
                    continue
                loc_info = json.loads(loc_jsons[0].text)[0]

                street_address = loc_info['address']['streetAddress']
                city = loc_info['address']['addressLocality']
                state = loc_info['address']['addressRegion']
                zip_code = loc_info['address']['postalCode']
                phone_number = loc_info['address']['telephone']

                lat = loc_info['geo']['latitude']
                longit = loc_info['geo']['longitude']
                coords.append((lat, longit))

                hours = loc_info['openingHours']
                location_name = loc_info['name']

                country_code = 'US'
                store_number = link.split('autoparts-')[1].replace('.html', '')
                
                location_type = '<MISSING>'
                store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code, 
                            store_number, phone_number, location_type, lat, longit, hours, page_url]
                all_store_data.append(store_data)
            
        search.max_count_update(coords)
        coord = search.next_coord()

    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
