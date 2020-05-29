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
    locator_domain = 'https://clicks.com/'

    driver = SgSelenium().chrome()
    driver.get(locator_domain)
    driver.implicitly_wait(20)
    all_store_data = []

    ##Corporate location
    divs = driver.find_elements_by_css_selector('div.clicks_locat')
    cont = divs[1].find_element_by_css_selector('div.block')
    content = cont.find_element_by_css_selector('p').text.split('\n')
    street_address = content[0]
    city, state, zip_code = addy_ext(content[1])
    phone_number = content[2]

    lat = '<MISSING>'
    longit = '<MISSING>'

    country_code = 'US'
    store_number = '<MISSING>'
    location_type = 'Corporate Office'
    location_name = 'Corporate Office'
    hours = '<MISSING>'

    store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code,
                  store_number, phone_number, location_type, lat, longit, hours]
    all_store_data.append(store_data)


    element = driver.find_element_by_css_selector('a.popmake-locations.pum-trigger')
    driver.execute_script("arguments[0].click();", element)

    places = driver.find_element_by_css_selector('ul.site_list')
    links = places.find_elements_by_css_selector('a')
    href_list = []
    for link in links:
        href_list.append(link.get_attribute('href'))






    for link in href_list:
        driver.get(link)
        driver.implicitly_wait(10)
        content = driver.find_element_by_css_selector('div.top-location').text.split('\n')
        location_name = '<MISSING>'
        street_address = content[0]
        city, state, zip_code = addy_ext(content[1])
        phone_number = content[2].replace('Ph:', '').strip()
        hours = ''
        for h in content[3:]:
            hours += h + ' '

        hours = hours.strip()

        lat = '<MISSING>'
        longit = '<MISSING>'

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
