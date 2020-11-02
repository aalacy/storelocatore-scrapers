import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import usaddress
import re 
import json
import _jsonnet

def parse_address(addy_string):
    parsed_add = usaddress.tag(addy_string)[0]

    street_address = ''

    if 'AddressNumber' in parsed_add:
        street_address += parsed_add['AddressNumber'] + ' '
    if 'StreetNamePreDirectional' in parsed_add:
        street_address += parsed_add['StreetNamePreDirectional'] + ' '
    if 'StreetNamePreType' in parsed_add:
        street_address += parsed_add['StreetNamePreType'] + ' '
    if 'StreetName' in parsed_add:
        street_address += parsed_add['StreetName'] + ' '
    if 'StreetNamePostType' in parsed_add:
        street_address += parsed_add['StreetNamePostType'] + ' '
        
    if 'ZipCode' not in parsed_add:
        zip_code = '<MISSING>'
    else:
        zip_code = parsed_add['ZipCode']

    return street_address, zip_code

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
    url = 'https://www.uhsinc.com/wp-content/themes/uhs/shortcodes/locationsmap/data.php?data=107005'
    res = session.get(url)
    locator_domain = 'https://www.uhsinc.com/'
    places = re.finditer(r'places.push\(([\s\S]+?)\);', res.text)
    all_store_data = []
    for place_match in places: 
        
        place_js = place_match.group(1)
        place_py = json.loads(_jsonnet.evaluate_snippet('snippet', place_js))
        location_type = place_py['type']
        location_name = re.match("<h3>(.*?)</h3>", place_py['tooltip_html']).group(1)
        if 'Hospital Panamericano' in location_name:
            continue
        lat = place_py['position']['lat']
        longit = place_py['position']['lng']
        html_to_parse = place_py['infowin_html']  
        
        if float(longit) > -10:
            continue

        soup = BeautifulSoup(html_to_parse, 'html.parser')
        info = soup.find('span', {'class': 'hidden'})
        try:
            page_url = info.find('a')['href']
        except:
            page_url = '<MISSING>'
        raw_info = info.prettify().split('\n')
        addy_phone = [i for i in raw_info if '<' not in i]

        city_state = addy_phone[0].split(',')
        if 'Guaynabo' in city_state[0]:
            street_address = 'Calle 1'
            state = 'Puerto Rico'
            zip_code = '00968'
            city = 'Guaynabo'
        else:
            if len(city_state) == 1:
                city_state = city_state[0].strip().split(' ')

            city = city_state[0].strip()
            state = city_state[1].strip()

            addy = addy_phone[1].replace('West Springville', '')

            street_address, zip_code = parse_address(addy)
            
        if len(addy_phone) == 2:
            phone_number = '<MISSING>'
        else:
            phone_number = addy_phone[2].replace('Phone:', '').strip()

        country_code = 'US'
        store_number = '<MISSING>'
        hours = '<MISSING>'
        
        if street_address.strip() == '':
            street_address = "<MISSING>"
        if 'Visit' in phone_number:
            phone_number = '<MISSING>'
        
        store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code, 
                    store_number, phone_number, location_type, lat, longit, hours, page_url]
        all_store_data.append(store_data)

    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
