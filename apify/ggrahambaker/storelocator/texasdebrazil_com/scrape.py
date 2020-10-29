import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import usaddress

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
    if 'OccupancyType' in parsed_add:
        street_address += parsed_add['OccupancyType'] + ' '
    if 'OccupancyIdentifier' in parsed_add:
        street_address += parsed_add['OccupancyIdentifier'] + ' '
        
    if 'PlaceName' not in parsed_add:
        city = '<MISSING>'
    else:
        city = parsed_add['PlaceName']
    
    if 'StateName' not in parsed_add:
        state = '<MISSING>'
    else:
        state = parsed_add['StateName']
        
    if 'ZipCode' not in parsed_add:
        zip_code = '<MISSING>'
    else:
        zip_code = parsed_add['ZipCode']

    return street_address, city, state, zip_code

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

    locator_domain = 'https://texasdebrazil.com/' 
    ext = 'locations/'
    r = session.get(locator_domain + ext, headers = HEADERS)

    soup = BeautifulSoup(r.content, 'html.parser')

    main = soup.find('div', {'id': 'locationbody'})
    states = main.find_all('div', {'class': 'faqs-entry'})

    link_list = []
    for state in states:
        if 'International' in state.find('h4').text:
            continue
        loc_links = state.find_all('a')
        for link in loc_links:
            link_list.append(locator_domain[:-1] + link['href'])

    all_store_data = []
    for link in link_list:
        # print(link)
        r = session.get(link, headers = HEADERS)
        soup = BeautifulSoup(r.content, 'html.parser')
        location_name = "Texas de Brazil - " + soup.find('h1', {'class': 'location-info__title'}).text.strip().split('\n')[0].strip().encode("ascii", "replace").decode().replace("?","-")
        if 'Coming Soon' in location_name:
            continue

        addy = soup.find('div', {'class': 'location-info__address'}).text.strip()

        street_address, city, state, zip_code = parse_address(addy)
        state = state.split(",")[0]
        
        glink = soup.find('a', {'class': 'location-info__link'})['href']
        
        start = glink.find('@')
        coords = glink[start + 1:].split(',')
        lat = coords[0]
        longit = coords[1]

        phone_number = soup.find('span', {'class': 'number-phone-desktop'}).text.strip()
        
        hours = ''
        for h in soup.find(class_="info-block__schedule").find_all('span', {'class': 'info-block__time'}):
            hours += h.text + ' '
            
        hours = hours.encode("ascii", "replace").decode().replace("?","-").strip()

        country_code = 'US'
        store_number = '<MISSING>'
        location_type = '<MISSING>'
        page_url = link
        
        store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code, 
                    store_number, phone_number, location_type, lat, longit, hours, page_url]

        all_store_data.append(store_data)
        
    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
