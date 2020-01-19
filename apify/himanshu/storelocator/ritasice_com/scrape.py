import csv
from sgrequests import SgRequests
import sgzip
import re

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36'
}
session = SgRequests()

search = sgzip.ClosestNSearch()
search.initialize()

def handle_missing(field):
    if field == None or (type(field) == type('x') and len(field.strip()) == 0):
        return '<MISSING>'
    return field

def parse_hours(hours):
    try:
        days = re.finall(r'<td>([a-zA-Z]+)<\\\/td>', hours)
        times = re.finall(r'<time>([ a-zA-Z0-9:-]+)<\\\/time>', hours)
        return ','.join(["{}: {}".format(x[0], x[1]) for x in zip(days, times)])
    except:
        return "<MISSING>"

def fetch_data():
    keys = set()
    coord = search.next_coord()
    while coord:
        result_coords = []
        query_lat, query_lng = coord[0], coord[1]
        r = session.get("https://www.ritasice.com/wp-admin/admin-ajax.php?action=store_search&lat={}&lng={}&max_results=200&search_radius=50".format(query_lat, query_lng),headers=HEADERS)
        location_list = r.json()
        for location in location_list:
            name = handle_missing(location['store'])
            street_address = handle_missing(location['address'])
            city = handle_missing(location['city'])
            state = handle_missing(location['state'])
            store_zip = handle_missing(location['zip'])
            store_id = handle_missing(location['id'])
            phone = handle_missing(location['phone'])
            hours = parse_hours(location['hours'])
            country = handle_missing(location['country'])
            lat = handle_missing(location['lat'])
            lng = handle_missing(location['lng'])
            if str(lat) == "0" or str(lng) == "0":
                lat = "<MISSING>"
                lng = "<MISSING>"
            else:
                result_coords.append((lat, lng))
            page_url = handle_missing(location['url'])
            store = []
            store.append("https://www.ritasice.com")
            store.append(name)
            store.append(street_address)
            key = "|".join([street_address, city, state, store_zip])
            if key in keys:
                continue
            keys.add(key)
            store.append(city)
            store.append(state)
            store.append(store_zip)
            store.append(country)
            store.append(store_id)
            store.append(phone)
            store.append("<MISSING>")
            store.append(lat)
            store.append(lng)
            store.append(hours)
            store.append(page_url)
            yield store
        if len(result_coords) > 0:
            search.max_count_update(result_coords)
        else:
            search.max_distance_update(30.0)
        coord = search.next_coord()

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
