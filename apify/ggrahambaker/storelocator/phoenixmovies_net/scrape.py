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

    return street_address.strip(), city.strip(), state.strip(), zip_code.strip()

def fetch_data():
    session = SgRequests()
    HEADERS = { 'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36' }

    locator_domain = 'https://phoenixmovies.net/' 

    r = session.get(locator_domain, headers = HEADERS)
    soup = BeautifulSoup(r.content, 'html.parser')

    locs = soup.find('div', {'class': 'theatre-set'}).find_all('a')
    link_list = [locator_domain[:-1] + l['href'] for l in locs]

    all_store_data = []
    for link in link_list:
        r = session.get(link, headers = HEADERS)
        soup = BeautifulSoup(r.content, 'html.parser')
        
        main = soup.find('div', {'id': 'theatre-information'})
        location_name = main.find('h1').text
        
        try:
            a_tag = main.find('p', {'class': 'address'}).find('a')
            google_link = a_tag['href']
            
            start = google_link.find('@')
            coords = google_link[start+1:].split(',')
            lat = coords[0]
            longit = coords[1]
        except:
            lat = '<MISSING>'
            longit = '<MISSING>'
        
        street_address, city, state, zip_code = parse_address(a_tag.text.strip())
        if street_address == "17310 Laurel Park Drive":
            street_address = "17310 Laurel Park Drive North"
        phone_number = soup.find('p', {'class': 'phone'}).text.replace("Virtual Spin Tour","").strip()
        country_code = 'US'
        store_number = link.split("/")[-1]
        location_type = '<MISSING>'
        hours = '<MISSING>'
        
        page_url = link
        
        store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code, 
                    store_number, phone_number, location_type, lat, longit, hours, page_url]
        all_store_data.append(store_data)
        
    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
