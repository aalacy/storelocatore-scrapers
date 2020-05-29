import csv
import os
from sgselenium import SgSelenium
import usaddress
import time

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
    locator_domain = 'https://houseofair.com/'
    ext = 'locations/'

    driver = SgSelenium().chrome()
    driver.get(locator_domain + ext)

    main = driver.find_element_by_css_selector('section#content-locations')
    locs = main.find_elements_by_css_selector('div.col-md-3')
    link_list = []
    for loc in locs:
        link = loc.find_element_by_css_selector('a').get_attribute('href')
        if '.pl/' in link:
            continue
        link_list.append(link)

    all_store_data = []
    for link in link_list:
        driver.get(link + 'trampoline-park/')
        time.sleep(3)
        driver.implicitly_wait(30)
        
        hours_ul = driver.find_element_by_xpath("//h3[contains(text(),'General Access')]/following-sibling::ul")
        
        hours = hours_ul.text.replace('\n', ' ').strip()
        
        contact_info = driver.find_element_by_xpath("//h2[contains(text(),'CONTACT')]/following-sibling::ul").text.split('\n')
        
        addy = contact_info[0]
        street_address, city, state, zip_code = parse_addy(addy)
        phone_number = contact_info[1]
        
        hrefs = driver.find_elements_by_xpath("//iframe[contains(@src, 'www.google.com/maps/')]")
        
        if len(hrefs) == 0:
            lat = '<MISSING>'
            longit = '<MISSING>'
        else:
            google_src = hrefs[0].get_attribute('src')
            start = google_src.find('!2d')
            if 'Old Mason' in street_address:
                end = google_src.find('!3m')
            else:
                end = google_src.find('!2m')
            coords = google_src[start + 3: end].split('!3d')
            
            lat = coords[1]
            longit = coords[0]
            
        page_url = link
        location_name = 'House of Air ' + city
        
        country_code = 'US'

        location_type = '<MISSING>'
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
