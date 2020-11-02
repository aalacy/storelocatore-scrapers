import csv
from sgrequests import SgRequests
import re
import json
import sgzip
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('allsups_com')


session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w',newline= "") as output_file:
        writer = csv.writer(output_file, delimiter=',',
                            quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    search = sgzip.ClosestNSearch()
    search.initialize()
    MAX_RESULTS = 150
    MAX_DISTANCE = 60
    current_results_len = 0  # need to update with no of count.
    coord = search.next_coord()
    locator_domain = "https://allsups.com/"
    addresses = [] 
    
    while coord:
        result_coords = []
        lat = coord[0]
        lng = coord[1]
        #logger.info("remaining zipcodes: " + str(search.zipcodes_remaining()))
        json_data = session.get("https://allsups.com/wp-admin/admin-ajax.php?action=store_search&lat="+str(lat)+"&lng="+str(lng)+"&max_results=100&search_radius=500").json()
        current_results_len = len(json_data)
        for data in json_data:
            location_name = data['store']
            street_address = (data['address']+" "+ str(data['address2']))
            city = data['city']
            state = data['state']
            zipp = data['zip']
            phone = data['phone']
            store_number = location_name.split()[-1].strip()
            latitude = data['lat']
            longitude = data['lng']

            result_coords.append((latitude,longitude))
            store = []
            store.append(locator_domain if locator_domain else '<MISSING>')
            store.append(location_name if location_name else '<MISSING>')
            store.append(street_address if street_address else '<MISSING>')
            store.append(city if city else '<MISSING>')
            store.append(state if state else '<MISSING>')
            store.append(zipp if zipp else '<MISSING>')
            store.append("US" if zipp.replace("-","").strip().isdigit() else "CA")
            store.append(store_number if store_number else '<MISSING>')
            store.append(phone if phone else '<MISSING>')
            store.append('<MISSING>')
            store.append(latitude if latitude else '<MISSING>')
            store.append(longitude if longitude else '<MISSING>')
            store.append('24-hour')
            store.append("<MISSING>")
            if store[2] in addresses:
                continue
            addresses.append(store[2])
            store = [str(x).encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]
            yield store

        if current_results_len < MAX_RESULTS:
            search.max_distance_update(MAX_DISTANCE)
        elif current_results_len == MAX_RESULTS:
            search.max_count_update(result_coords)
        else:
            raise Exception("expected at most " + str(MAX_RESULTS) + " results")
        coord = search.next_coord()
def scrape():
    data = fetch_data()
    write_output(data)


scrape()
