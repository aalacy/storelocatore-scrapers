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

    locator_domain = 'https://www.muji.com/' 
    url = 'https://www.muji.com/storelocator/?_ACTION=_SEARCH&c=ca&lang=LC&swLat=18.361370319683378&swLng=-165.69671737502938&neLat=67.0873584048944&neLng=-52.493592375029394'
    r = session.get(url, headers = HEADERS)
    all_n_america = json.loads(r.content)
    all_store_data = []
    for loc in all_n_america:
        shopid = loc['shopid']
        country_code = shopid[:2]
        store_number = shopid[2:]
        if country_code != 'US':
            continue
            
        location_name = loc['shopname']
        addy = loc['shopaddress'].split(',')
        
        if len(addy) == 6:
            street_address = addy[3].strip()
            city = addy[4].strip()
            zip_state = addy[5].strip().split(' ')
            state = zip_state[0]
            zip_code = zip_state[1]
            
        elif len(addy) == 4:
            if '2936 MAIN STREET' in addy[0]:
                street_address = addy[0].strip()
                city = addy[1].strip()
                state = addy[2].strip()
                zip_code = addy[3].strip()
            else:
                if '170 SOUTH MARKET STREET' in addy[0]:
                    street_address = addy[0].strip() + ' ' + addy[1].strip()

                else:
                    street_address = addy[1].strip()
                city = addy[2].strip()
                zip_state = addy[3].strip().split(' ')
                state = zip_state[0]
                zip_code = zip_state[1]
        elif len(addy) == 3:
            street_address = addy[0].strip()
            city = addy[1].strip()
            zip_state = addy[2].strip().split(' ')
            
            state = zip_state[0]
            if len(zip_state) == 1:
                zip_code = '<MISSING>'
            else:
                zip_code = zip_state[1]
        else:
            street_address = '1345 3rd Street Promenade'
            city = 'Santa Monica'
            zip_state = addy[1].strip().split(' ')
            state = zip_state[0]
            zip_code = zip_state[1]
            
        if '7021HOLLYWOOD' in street_address:
            street_address = '7021 HOLLYWOOD BOULEVARD'
        hours = loc['opentime'].replace('\u3000', ' ')
        phone_number = loc['tel'].replace('\u3000', ' ').strip()
        if phone_number == '':
            phone_number = '<MISSING>'
        lat = loc['latitude']
        longit = loc['longitude']
        
        store_number = '<MISSING>'
        location_type = '<MISSING>'
        page_url = '<MISSING>'
        
        store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code, 
                    store_number, phone_number, location_type, lat, longit, hours, page_url]
                    
        all_store_data.append(store_data)

    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
