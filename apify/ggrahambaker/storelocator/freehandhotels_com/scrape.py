import csv
import os
from sgselenium import SgSelenium
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('freehandhotels_com')



def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
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
    locator_domain = 'https://freehandhotels.com/'

    driver = SgSelenium().chrome()
    driver.get(locator_domain)

    ul = driver.find_element_by_css_selector('ul#menu-global-navigation')
    lis = ul.find_elements_by_css_selector('li')
    link_list = []
    for li in lis:
        link = li.find_element_by_css_selector('a').get_attribute('href')
        if 'eat-' in link:
            continue
        if 'blog' in link:
            continue

        link_list.append(link)

    all_store_data = []
    for link in link_list:
        #logger.info(link)
        driver.get(link)
        driver.implicitly_wait(10)
        loc_div = driver.find_element_by_css_selector('div.location.active-menu.limitFix')
        coords_link = loc_div.find_element_by_css_selector('a.location__col.static_map').get_attribute('href')

        start = coords_link.find('/@') + 2
        end = coords_link.find('z/data')
        coords = coords_link[start:end].split(',')
        lat = coords[0]
        longit = coords[1]

        location_name = loc_div.find_element_by_css_selector('h2.location__name').text

        addy = loc_div.find_element_by_css_selector('address').text.split('\n')
        street_address = addy[0]
        city, state, zip_code = addy_ext(addy[1])
        phone_number = addy[2]

        country_code = 'US'
        store_number = '<MISSING>'
        location_type = '<MISSING>'
        hours = '<MISSING>'

        store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code,
                      store_number, phone_number, location_type, lat, longit, hours,link]
        all_store_data.append(store_data)

    driver.quit()
    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
