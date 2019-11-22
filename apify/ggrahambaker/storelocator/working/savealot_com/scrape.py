import csv
import requests
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
    locator_domain = 'https://savealot.com/'
    day_lookup = {0: 'Monday', 1: 'Tuesday', 2: 'Wednesday', 3: 'Thursday', 4: 'Friday', 5: 'Saturday', 6: 'Sunday'}
    loc_json_url = 'https://savealot.com/grocery-stores/locationfinder/modules/multilocation/?near_lat=47.600392&near_lon=-122.3353602&threshold=4000&services__in=&within_business=true'

    page = requests.get(loc_json_url)
    loc_json = json.loads(page.content)

    all_store_data = []
    for loc in loc_json['objects']:
        phone_number = loc['phonemap_e164']['phone']
        state = loc['state']
        street_address = loc['street']
        zip_code = loc['postal_code']
        page_url = loc['location_url']
        longit = loc['lon']
        lat = loc['lat']
        city = loc['city']

        hours_arr = loc['hours_of_operation']
        hours = ''
        for i, day in enumerate(hours_arr):
            day_start = day[0][0]
            day_end = day[0][1]
            day_hours = day_lookup[i] + ' ' + day_start + ' : ' + day_end + ' '
            hours += day_hours

        hours = hours.strip()

        country_code = 'US'
        location_name = '<MISSING>'
        location_type = '<MISSING>'
        store_number = '<MISSING>'

        store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code,
                      store_number, phone_number, location_type, lat, longit, hours, page_url]
        all_store_data.append(store_data)

    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
