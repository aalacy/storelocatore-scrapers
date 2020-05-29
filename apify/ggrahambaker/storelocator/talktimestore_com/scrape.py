import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import usaddress

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def parse_address(addy_string):
    parsed_add = usaddress.tag(addy_string)[0]

    street_address = ''

    if 'AddressNumber' in parsed_add:
        street_address += parsed_add['AddressNumber'] + ' '
    if 'StreetNamePreDirectional' in parsed_add:
        street_address += parsed_add['StreetNamePreDirectional'] + ' '
    if 'StreetName' in parsed_add:
        street_address += parsed_add['StreetName'] + ' '
    if 'StreetNamePostType' in parsed_add:
        street_address += parsed_add['StreetNamePostType'] + ' '
    if 'OccupancyType' in parsed_add:
        street_address += parsed_add['OccupancyType'] + ' '
    if 'OccupancyIdentifier' in parsed_add:
        street_address += parsed_add['OccupancyIdentifier'] + ' '
    city = parsed_add['PlaceName']
    state = parsed_add['StateName']
    zip_code = parsed_add['ZipCode']

    return street_address, city, state, zip_code

def fetch_data():
    session = SgRequests()
    HEADERS = { 'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36' }

    locator_domain = 'https://www.talktimestore.com/' 
    ext = 'storelocator/'    

    r = session.get(locator_domain + ext, headers = HEADERS)
    soup = BeautifulSoup(r.content, 'html.parser')
    
    locs = soup.find('ul', {'class': 'stores'}).find_all('li')

    all_store_data = []
    for loc in locs:
        page_url = loc.find('a', {'class': 'store-logo'})['href']
        
        r = session.get(page_url, headers = HEADERS)
        
        source = str(r.content.decode())
        for line in source.split('\n'):
            if line.strip().startswith("var storeLat"):
                lat = line.strip().replace('var storeLat =', '').replace(';', '').strip()
            if line.strip().startswith("var storeLong"):
                longit = line.strip().replace('var storeLong =', '').replace(';', '').strip()
            
        soup = BeautifulSoup(r.content, 'html.parser')
        location_name = soup.find('h1', {'class': 'page-header'}).text
        
        tds = soup.find_all('td')
        for i, td in enumerate(tds):
            if 'Address' in td.text:
                addy = tds[i + 1].text
                
                if '30131 U.S. 19 N.' in addy:
                    street_address = '30131 U.S. 19 N.'
                    city = 'Clearwater'
                    state = 'Florida'
                    zip_code = '33761'
                elif '36603 U.S. 19' in addy:
                    street_address = '36603 U.S. 19'
                    city = 'Palm Harbor'
                    state = 'Florida'
                    zip_code = '34684'
                elif '14821 U.S. HWY 301' in addy:
                    street_address = '14821 U.S. HWY 301'
                    city = 'Dade City'
                    state = 'Florida'
                    zip_code = '33523'
                elif '8868 FL-52' in addy:
                    street_address = '8868 FL-52'
                    city = 'Hudson'
                    state = 'Florida'
                    zip_code = '34667'
                elif '27001 US Hwy 19 N #2072' in addy:
                    street_address = '27001 US Hwy 19 N #2072'
                    city = 'Clearwater' 
                    state = 'Florida'
                    zip_code = '33761'
                elif '6139 State Road 54' in addy:
                    street_address = '6139 State Road 54 New Port' 
                    city = 'Richey'
                    state = 'Florida'
                    zip_code = '34653'
                    
                elif '21631 Village Lakes' in addy:
                    street_address = '21631 Village Lakes Shopping Center Drive'
                    city = 'Land O Lakes'
                    state = 'Florida'
                    zip_code = '34639'
                    
                else:
                    street_address, city, state, zip_code = parse_address(tds[i + 1].text)
                
                country_code = 'US'
            if 'Phone' in td.text:
                phone_number = tds[i + 1].text
            
            if 'Monday' in td.text:
                hours_table = tds[i].parent.parent.find_all('tr')
                hours = ''
                for row in hours_table:
                    tds = row.find_all('td')
                    for td in tds:
                        hours += td.text + ' '
                        
        store_number = '<MISSING>'
        location_type = '<MISSING>'
        
        store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code,
                    store_number, phone_number, location_type, lat, longit, hours, page_url]

        all_store_data.append(store_data)

    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
