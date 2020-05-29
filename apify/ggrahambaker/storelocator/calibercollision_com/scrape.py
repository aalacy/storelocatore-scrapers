import csv
from sgrequests import SgRequests
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

    locator_domain = 'https://calibercollision.com/' 

    url = 'https://calibercollision.com/api/locations'
    r = session.get(url, headers = HEADERS)
    loc_json = json.loads(r.content)['entries']

    all_store_data = []
    for loc in loc_json:

        location_name = loc['title']

        if 'No Location' in location_name:
            continue
        if 'hours' not in loc:
            if 'newTime_open' not in loc:
                hours = 'By Appointment Only'
            
            else:
                if 'newTime_closed' not in loc:
                    hours = '<MISSING>'
                else:
                    hours = loc['newTime_open'] + '-' + loc['newTime_closed'] + ' M-F ' 
                    if 'CLOSED' in loc['newTime_open_saturday']:
                        hours += loc['newTime_open_saturday'].replace('&amp;', '&')
                    else:
                        hours += loc['newTime_open_saturday'] + '-' + loc['newTime_closed_saturday']
                        
        elif loc['hours'].strip() == '':
            hours = loc['newTime_open'] + '-' + loc['newTime_closed'] + ' M-F ' 
            hours += loc['newTime_open_saturday'] + '-' + loc['newTime_closed_saturday']
        
        else:
            hours_raw = loc['hours'].replace('\n', ' ').replace('<br />', ' ').replace('<br>', ' ').replace('<br/>', ' ').strip()
            hours = ' '.join(hours_raw.split())
            if 'SAT' not in hours:
                hours += ' ' + loc['newTime_open_saturday'] + '-' + loc['newTime_closed_saturday']

        if 'SUN' not in hours:
            if 'Appointment' not in hours:
                hours += ' CLOSED SUN'
        hours = hours.strip().replace('&amp;', '&').replace('SUN-', 'SUN')

        addy = loc['address_info'][0]
        street_address = addy['address']
        city = addy['city']
        state = addy['state_province']
        zip_code = addy['zip']
        
        phone_number = addy['phone']
        
        lat = addy['latitude']
        longit = addy['longitude']
        
        country_code = 'US'
        
        store_number = '<MISSING>'
        location_type = '<MISSING>'
        
        page_url = locator_domain[:-1] + loc['url']
        
        store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code, 
                    store_number, phone_number, location_type, lat, longit, hours, page_url]

        all_store_data.append(store_data)

    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
