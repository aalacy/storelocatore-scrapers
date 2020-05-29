import csv
import os
from sgselenium import SgSelenium
import json
from selenium.webdriver.support.ui import Select
import time
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
    locator_domain = 'https://www.palmettohealth.org/'
    ext = 'locations-directions'

    driver = SgSelenium().chrome()
    driver.get(locator_domain + ext)
    driver.implicitly_wait(10)
    time.sleep(5)

    options = driver.find_element_by_id('p_lt_ctl01_pageplaceholder_p_lt_ctl02_LocationsSearch_CategoryID').find_elements_by_css_selector('option')

    opts = [[opt.get_attribute('value'), opt.text] for opt in options]
    all_store_data = []
    for opt in opts:
        select = Select(driver.find_element_by_id('p_lt_ctl01_pageplaceholder_p_lt_ctl02_LocationsSearch_CategoryID'))

        val = opt[0]
        location_type = opt[1]

        select.select_by_value(val)
        
        but = driver.find_element_by_css_selector('a.go-btn')

        driver.execute_script("arguments[0].click();", but)
        time.sleep(2)
        
        source = str(driver.page_source)
        for line in source.split('\n'):
            if line.strip().startswith("var locations"):
                info = str(line.strip()).replace('var locations = ', '').replace(';', '')
                j_loc = json.loads(info)

        for loc in j_loc:
            lat = loc[2]
            longit = loc[3]
            
            html = loc[5]
            soup = BeautifulSoup(html, 'html.parser')
            
            rows = soup.find_all('tr')
            
            location_name = rows[0].find_all('td')[1].text.strip()
            addy = rows[1].find_all('td')[1].text.strip()

            street_address, city, state, zip_code = parse_address(addy)

            if street_address.strip() == '':
                street_address = '<MISSING>'

            if ',' in city:
                city = city.split(',')[1]

            phone_number = rows[2].find_all('td')[1].text.strip()
            
            if phone_number == '':
                phone_number = '<MISSING>'
    
            hours = rows[3].find_all('td')[1].text.strip()
            if hours == '':
                hours = '<MISSING>'
    
            country_code = '<MISSING>'
            store_number = '<MISSING>'
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
