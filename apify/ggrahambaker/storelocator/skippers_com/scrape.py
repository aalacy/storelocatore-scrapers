import csv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import json
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


def get_driver():
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--window-size=1920,1080')
    return webdriver.Chrome('chromedriver', options=options)




def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    locator_domain = 'https://skippers.com/'
    url = 'https://skippers.com/wp-json/wpgmza/v1/markers/base64eJyrVkrLzClJLVKyUqqOUcpNLIjPTIlRsopRMoxR0gEJFGeUgsSKgYLRsbVKtQCV7hBN'
        
    driver = get_driver()
    driver.get(locator_domain)
    driver.get(url)
    driver.implicitly_wait(10)
    loc_info = json.loads(driver.find_element_by_css_selector('body').text)

    all_store_data = []
    for loc in loc_info:
        location_name = loc['title']
        store_number = loc['id']
        street_address, city, state, zip_code = parse_address(loc['address'].replace(', USA', '').strip())

        state = state.replace(', USA', '').strip()

        loc['description']
        
        phone_number = loc['description'].strip()
        if phone_number == '':
            phone_number = '<MISSING>'
        else:
            soup = BeautifulSoup(phone_number, 'html.parser')
            phone_number = soup.find('p').text.strip()
        
        lat = loc['lat']
        longit = loc['lng']
        country_code = 'US'
        
        location_type = '<MISSING>'
        hours = '<MISSING>'
        page_url = '<MISSING>'
        store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code, 
                    store_number, phone_number, location_type, lat, longit, hours, page_url]


        all_store_data.append(store_data)






    driver.quit()
    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
