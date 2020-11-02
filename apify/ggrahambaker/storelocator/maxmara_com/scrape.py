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

    locator_domain = 'https://maxmara.com/' 
    us_url = 'https://us.maxmara.com/store-locator?south=-37.85012759632715&west=-149.62984375&north=77.04151444711106&east=-41.70015625&name=&listJson=true&withoutRadius=false&country=US'
    can_url = 'https://ca.maxmara.com/store-locator?south=-52.08464201527304&west=-170.443359375&north=86.91057206489693&east=-21.556640625000018&name=&listJson=true&withoutRadius=false&country=CA'
    urls = [us_url, can_url]
    all_store_data = []
    for url in urls:
        r = session.get(url , headers = HEADERS)
        locs = json.loads(r.content)['features']
        for loc in locs:
            props = loc['properties']
            zip_code = props['zip']
            if 'United States' in props['country']:
                country_code = 'US'
            else:
                country_code = 'CA'
                
            lat = props['lat']
            longit = props['lng']
            city = props['city']
            addy_split = props['formattedAddress'].split(',')
            state = addy_split[1]
            
            for d in addy_split[2]:
                if d.isdigit():
                    state = '<MISSING>'
                    break

            location_name = props['displayName']
            
            phone_number = props['phone1']
            
            street_address = props['formattedAddress'].split(',')[0]
      
            hours = ''
                
            for day, val in props['openingHours'].items():
                
                hours += day + ' ' + val[0] +  ' '       
        
            hours = hours.strip()

            page_url = 'https://world.maxmara.com/store/' + str(props['name'])
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
