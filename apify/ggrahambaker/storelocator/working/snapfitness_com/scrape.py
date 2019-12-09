import csv
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
import usaddress
import time


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


def parse_addy(addy):
    parsed_add = usaddress.tag(addy)[0]

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

    street_address = street_address.strip()
    city = parsed_add['PlaceName'].strip()
    state = parsed_add['StateName'].strip()
    zip_code = parsed_add['ZipCode'].strip()
    
    return street_address, city, state, zip_code


def fetch_data():
    locator_domain = 'https://www.snapfitness.com/'

    driver = get_driver()
    driver.get('https://www.snapfitness.com/us/gyms/?q=united%20states')
    time.sleep(5)
    link_list = []
    locs = driver.find_elements_by_css_selector('div.club-overview')
    for loc in locs:
        href = loc.find_element_by_css_selector('a.btn.btn-primary').get_attribute('href')
        if href not in link_list:
            link_list.append(href)


    all_store_data = []
    for i, link in enumerate(link_list):
        driver.get(link)
        driver.implicitly_wait(10)
        
        main = driver.find_element_by_css_selector('div.details')
        location_name = main.find_element_by_css_selector('h3').text
        phone_number = main.find_element_by_css_selector('a.link_phonenumber').text.strip()
        if phone_number == '':
            phone_number = '<MISSING>'
        
        addy = driver.find_elements_by_css_selector('div.content-holder')[2].text.replace('\n', ' ')
        if '1433 B (68 Place) Highway 68 North' in addy:
            street_address = '1433 B (68 Place) Highway 68 North' 
            city = 'Oak Ridge'
            state = 'NC'
            zip_code = '27310'
        elif '1515 US-22' in addy:
            street_address = '1515 US-22'
            city = 'Watchung'
            state = 'NJ'
            zip_code = '07069'

        else:
            street_address, city, state, zip_code = parse_addy(addy)
        
        
        google_href = driver.find_element_by_css_selector('a#map').get_attribute('href')
        
        start = google_href.find('&query=')
        coords = google_href[start + len('&query='):].split(',')

        lat = coords[0]
        longit = coords[1]
        try:
            hours = driver.find_element_by_css_selector('section#overviewSection').find_element_by_css_selector('h2').text
        except NoSuchElementException:
            hours = 'Open 24/7 to members'
        
        country_code = 'US'

        location_type = '<MISSING>'
        page_url = link

        store_number = '<MISSING>'

        store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code,
                        store_number, phone_number, location_type, lat, longit, hours, page_url]
        all_store_data.append(store_data)



    driver.quit()
    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
