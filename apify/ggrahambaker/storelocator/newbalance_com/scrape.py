import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import sgzip
import json
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('newbalance_com')



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
    locator_domain = 'https://www.newbalance.com/'

    search = sgzip.ClosestNSearch()
    search.initialize(country_codes = ['ca', 'us'])

    coord = search.next_coord()
    dup_tracker = set()

    all_store_data = []
    while coord:
        #logger.info("remaining zipcodes: " + str(search.zipcodes_remaining()))
        x = coord[0]
        y = coord[1]
        #logger.info('Pulling Lat-Long %s,%s...' % (str(x), str(y)))
        url = 'https://newbalance.locally.com/stores/conversion_data?has_data=true&company_id=41&store_mode=&style=&color=&upc=&category=&inline=1&show_links_in_list=&parent_domain=&map_center_lat=' + str(x) + '&map_center_lng=' + str(y) + '&map_distance_diag=100&sort_by=proximity&no_variants=0&only_retailer_id=&dealers_company_id=&only_store_id=false&uses_alt_coords=false&q=&zoom_level=10'
        #logger.info(url)
        r = session.get(url, headers=HEADERS)
        
        res_json = json.loads(r.content)['markers']

        result_coords = []
        
        for loc in res_json:
            lat = loc['lat']
            longit = loc['lng']

            if 'New Balance' in loc['name']:
                location_name = loc['name']
                
                if location_name not in dup_tracker:
                    dup_tracker.add(location_name)
                else:
                    continue

                street_address = loc['address'].split('--- ')[-1].strip()

                city = loc['city']
                state = loc['state']
                zip_code = loc['zip']
                country_code = loc['country']
                try:
                    phone_number = loc['phone_link'].replace('+1', '').replace('tel:', '').strip()

                except:
                    phone_number = '<MISSING>'

                if phone_number == '':
                    phone_number = '<MISSING>'

                slug = loc['slug']
                if slug == '':
                    page_url = 'https://stores.newbalance.com/shop/' + str(loc['id']) + '/' + location_name.lower().split('|')[0].replace(' ', '-')
                else:
                    page_url = 'https://stores.newbalance.com/shop/' + slug
                
                cat = str(loc['enhanced_categories']).split(':')[0].replace('{', '').replace("'", '')
                
                try:
                    location_type = loc['enhanced_categories'][cat]['value']
                except:
                    location_type = '<MISSING>'
                r = session.get(page_url, headers=HEADERS)
                
                if page_url == 'https://stores.newbalance.com/shop/new-balance':
                    hours = '<MISSING>'
                else:    
                    soup = BeautifulSoup(r.content, 'html.parser')
                    app_json_html = soup.find('script', {'type': "application/ld+json"})
                    loc_json = json.loads(app_json_html.text)
                    
                    if 'openingHours' not in loc_json:
                        hours = '<MISSING>'
                    else:
                        hours = ''
                        for h in loc_json['openingHours']:
                            hours += h + ' '

                        hours = hours.strip()
                
                store_number = '<MISSING>'
          
                store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code, 
                            store_number, phone_number, location_type, lat, longit, hours, page_url]

                all_store_data.append(store_data)
                
            result_coords.append((lat, longit))
        
        search.max_count_update(result_coords)
        coord = search.next_coord()  

    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
