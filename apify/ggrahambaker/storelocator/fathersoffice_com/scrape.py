import csv
import os
from sgselenium import SgSelenium

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)

def addy_ext(addy):
    address = addy.split(',')
    city = address[0]
    state_zip = address[1].strip().split(' ')
    state = state_zip[0]
    zip_code = state_zip[1]
    return city, state, zip_code

def fetch_data():
    # Your scraper here
    locator_domain = 'https://fathersoffice.com/'

    driver = SgSelenium().chrome()
    driver.get(locator_domain)
    driver.implicitly_wait(30)

    a_tags = driver.find_elements_by_css_selector('a.c-post.c-post--small')

    link_list = []
    for a_tag in a_tags:
        link_list.append(a_tag.get_attribute('href'))

    all_store_data = []
    for link in link_list:
        driver.get(link)
        driver.implicitly_wait(10)

        content = driver.find_element_by_css_selector('section.c-location-info').text.split('\n')

        if '905 E. 2ND ST.' in content[1]:
            # not open
            continue

        street_address = content[1]
        city, state, zip_code = addy_ext(content[2])
        phone_number = content[3]
        hours = ''
        for h in content[6:]:
            hours += h + ' '

        lat = '<MISSING>'
        longit = '<MISSING>'
        location_name = link[link.find('on/') + 3:].replace('-', ' ').replace('/', '')
        country_code = 'US'
        store_number = '<MISSING>'
        location_type = '<MISSING>'

        store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code,
                      store_number, phone_number, location_type, lat, longit, hours]
        all_store_data.append(store_data)

    driver.quit()
    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
