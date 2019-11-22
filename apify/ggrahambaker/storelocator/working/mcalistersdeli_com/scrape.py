import csv
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import usaddress


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
    locator_domain = 'https://www.mcalistersdeli.com/'
    ext = 'locations'

    driver = get_driver()
    driver.get(locator_domain + ext)
    driver.implicitly_wait(10)


    main = driver.find_element_by_css_selector('div.national-list').find_element_by_css_selector('ul')
    states = main.find_elements_by_css_selector('li')
    state_links = []
    for state in states:
        state_link = state.find_element_by_css_selector('a').get_attribute('href')
        state_links.append(state_link)    


    loc_list = []
    for state in state_links:
        driver.get(state)
        driver.implicitly_wait(10)
        main = driver.find_element_by_css_selector('div.state-national-list').find_element_by_css_selector('ul')
        cities = main.find_elements_by_css_selector('li')
        for city in cities:

            city_link = city.find_element_by_css_selector('a').get_attribute('href')
            loc_list.append(city_link)    
            


    link_list = []
    for loc in loc_list:
        driver.get(loc)
        driver.implicitly_wait(10)

        main = driver.find_element_by_css_selector('div.city-list').find_element_by_css_selector('ul')
        locs = main.find_elements_by_css_selector('li')
        for loc in locs:
            loc_links = loc.find_elements_by_css_selector('a')
            link = loc_links[0].get_attribute('href')
            loc_name = loc_links[0].text
            phone_number = loc_links[1].get_attribute('href').replace('tel:', '')
            link_list.append([link, loc_name, phone_number])    

            
        
    all_store_data = []
    for data in link_list:
        driver.get(data[0])
        driver.implicitly_wait(10)

        
        map_href = driver.find_element_by_xpath("//a[contains(@href, 'maps.google.com/?daddr')]").get_attribute('href')
        map_link_start = map_href.find('?daddr=')
        addy = map_href[map_link_start + 7:].replace('+', ' ')

        if '99 Eglin Parkway NE Ft.' in addy:
            street_address = '99 Eglin Parkway NE'
            city = 'Ft. Walton Beach'
            state = 'FL'
            zip_code = '32547'
        else:
            street_address, city, state, zip_code = parse_addy(addy)
        

        
        google_href = driver.find_element_by_xpath("//a[contains(@href, '/locations-search?AddressLatitude')]").get_attribute('href')
        start = google_href.find('AddressLatitude=')
        if start > 0:
            end = google_href.find('&id')
            coords = google_href[start + len('AddressLatitude=') : end].split('&AddressLongitude=')
            lat = coords[0]
            longit = coords[1]
            
        
        hours = driver.find_element_by_css_selector('div.hours-wrapper').text.replace('\n', ' ')

        
        country_code = 'US'

        location_type = '<MISSING>'
        page_url = data[0]
        store_number = '<MISSING>'
        location_name = data[1]
        phone_number = data[2]
        
        store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code,
                        store_number, phone_number, location_type, lat, longit, hours, page_url]
        
        
        all_store_data.append(store_data)
        
        

    driver.quit()
    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
