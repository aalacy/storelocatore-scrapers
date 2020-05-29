import csv
import os
from sgselenium import SgSelenium
from selenium.common.exceptions import NoSuchElementException
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

def parse_can_addy(addy):
    street_address = addy[0]
    rest_addy = addy[1].split(' ')
    city = rest_addy[0]
    state = rest_addy[1]
    zip_code = rest_addy[2] + ' ' + rest_addy[3]
    return street_address, city, state, zip_code

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

    driver = SgSelenium().chrome()
    urls = ['https://www.snapfitness.com/ca/gyms/?q=canada', 'https://www.snapfitness.com/us/gyms/?q=united%20states']
    all_store_data = []
    for url in urls:

        driver.get(url)
        
        time.sleep(5)
        go = driver.find_element_by_xpath("//button[contains(text(),'Go')]")
        driver.execute_script("arguments[0].click();", go)

        driver.implicitly_wait(10)
        time.sleep(3)
        link_list = []
        locs = driver.find_elements_by_css_selector('div.club-overview')
        
        for loc in locs:
            href = loc.find_element_by_css_selector('a.btn.btn-primary').get_attribute('href')
            if href not in link_list:
                link_list.append(href)



        for i, link in enumerate(link_list):
            
            driver.get(link)
    
            driver.implicitly_wait(10)
            
            main = driver.find_element_by_css_selector('div.location')
            try:
                location_name = main.find_element_by_css_selector('h1').text
                off = 0
            except NoSuchElementException:
                location_name = main.find_element_by_css_selector('h3').text
                off = 1

            conts = main.find_elements_by_css_selector('li')
            phone_number = conts[0 + off].text

            addy = conts[1 + off].text


            if '/ca/' in url:
                country_code = 'CA'
                addy = addy.split('\n')
                
                street_address, city, state, zip_code = parse_can_addy(addy)
            else:
                country_code = 'US'
                

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
                elif '10342 Dyno Dr, North Country Mall' in addy:
                    street_address = '10342 Dyno Dr, North Country Mall'
                    city = 'Hayward'
                    state = 'WI'
                    zip_code = '54843'
                elif '107 Waterstradt Commerce Dr' in addy:
                    street_address = '107 Waterstradt Commerce Dr, Unit A and B'
                    city = 'Dundee'
                    state = 'MI'
                    zip_code = '48131'

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
