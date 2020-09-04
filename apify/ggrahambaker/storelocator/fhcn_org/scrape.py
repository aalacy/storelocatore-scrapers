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

def addy_ext(addy):
    addy = addy.split(',')
    if len(addy) == 1:
        addy = addy[0].split(' ')
        city = addy[0]
        state = addy[1]
        zip_code = addy[2]
    else:
        city = addy[0]
        state_zip = addy[1].strip().split(' ')
        state = state_zip[0]
        zip_code = state_zip[1]
    return city, state, zip_code

def fetch_data():
    session = SgRequests()
    HEADERS = { 'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36' }

    locator_domain = 'https://www.fhcn.org/' 
    ext = 'locations/'
    r = session.get(locator_domain + ext, headers = HEADERS)

    soup = BeautifulSoup(r.content, 'html.parser')

    locs = soup.find_all('div', {'class': 'location_detail'})

    all_store_data = []

    for loc in locs:
        location_type = loc.find('div', {'class': 'location-services'}).text.strip()
        if 'Non-' in location_type:
            continue
            
        location_name = loc.find('div', {'class': 'location_detail_title'}).text.strip()
        if 'Mobile' in location_name:
            continue
        
        addy_raw = loc.find('div', {'class': 'address-wrapper'}).prettify().split('\n')
        addy = [a.strip() for a in addy_raw if '<' not in a]

        if '3505 E. Shields Ave. Fresno, CA 93726' in addy[1]:
            addy[1] = '3505 E. Shields Ave, Fresno, CA 93726'
        if '1008 N. Cherry St. Tulare, CA 93274' in addy[1]:
            addy[1] = '1008 N. Cherry St, Tulare, CA 93274'
        if len(addy) == 3:
            if '7060 N. Recreation Ave' in addy[1]:
                street_address = '7060 N. Recreation Ave #101'
                city, state, zip_code = '<MISSING>', '<MISSING>', '<MISSING>'
                
            else:  
                addy = addy[1].split(',')
                street_address = addy[0]
                try:
                    city = addy[1]
                    state_zip = addy[2].strip().split(' ')
                    state = state_zip[0]
                    zip_code = state_zip[1]
                except:
                    city = '<MISSING>'
                    state= '<MISSING>'
                    zip_code = '<MISSING>'
        else:
            street_address = addy[1]
            city, state, zip_code = addy_ext(addy[2])
        
        hours_raw = loc.find('div', {'class': 'hours-wrapper'}).find('div').prettify().split('\n')
        hours_arr = [h for h in hours_raw if '<' not in h]
        hours = ''
        for h in hours_arr:
            if 'Hours' in h:
                continue
            hours += h.strip().replace('&amp;', '&') + ' '
        
        hours = hours.strip()
        try:
            phone_number = loc.find('div', {'class': 'phone-wrapper'}).find('span').text

        except:
            phone = '<MISSING>'
        country_code = 'US'
        lat = '<MISSING>'
        longit = '<MISSING>'
        page_url = 'https://www.fhcn.org/locations/'
        store_number = '<MISSING>'
        if phone_number.find('KID') > -1:
            phone_number = phone_number.replace(' (KIDS)','')
        store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code, 
                    store_number, phone_number, location_type, lat, longit, hours, page_url]
        #print(store_data)
        all_store_data.append(store_data)

    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
