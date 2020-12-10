import csv
import sgzip 
import json
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

    search = sgzip.ClosestNSearch() # TODO: OLD VERSION [sgzip==0.0.55]. UPGRADE IF WORKING ON SCRAPER!
    search.initialize()
    locator_domain = 'https://www.cometcleaners.com/'

    MAX_RESULTS = 100
    MAX_DISTANCE = 500

    coord = search.next_coord()
    dup_tracker = set()
    all_store_data = []
    while coord:
        x = coord[0]
        y = coord[1]
        url = 'https://www.cometcleaners.com/wp-admin/admin-ajax.php?action=store_search&lat=' + str(x) + '&lng=' + str(y) + '&max_results=' + str(MAX_RESULTS) + '&search_radius=' + str(MAX_DISTANCE)
        r = session.get(url, headers=HEADERS)
        
        res_json = json.loads(r.content)
        result_coords = []
        result_coords.append((x, y))
        
        for loc in res_json:
            lat = loc['lat']
            longit = loc['lng']
            store_number = loc['id']
            result_coords.append((lat, longit))
            if store_number not in dup_tracker:
                dup_tracker.add(store_number)
            else:
                continue
            
            location_name = loc['store']
            street_address = loc['address'] + ' ' + loc['address2']
            street_address = street_address.strip()
            city = loc['city']
            state = loc['state']
            zip_code = loc['zip']
            if 'United States' in loc['country']:
                country_code = 'US'
            else:
                continue
                
            phone_number = loc['phone']
            if len(phone_number) == 15:
                continue
            hours_table = loc['hours']
            
            soup = BeautifulSoup(hours_table, 'html.parser')

            rows = soup.find_all('tr')
            hours = ''
            for r in rows:
                cols = r.find_all('td')
                day = cols[0].text
                time = cols[1].text
                hours += day + ' ' + time + ' '
                
            hours = hours.strip()
            
            page_url = loc['url']
            location_type = '<MISSING>'
            
            store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code, 
                        store_number, phone_number, location_type, lat, longit, hours, page_url]
            all_store_data.append(store_data)
            
        if len(res_json) < MAX_RESULTS:
            search.max_distance_update(MAX_DISTANCE)
        elif len(res_json) == MAX_RESULTS:
            search.max_count_update(result_coords)
        else:
            raise Exception("expected at most " + MAX_RESULTS + " results")
        coord = search.next_coord()  

    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
