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

def fetch_data():
    locator_domain = 'https://www.sonesta.com/'
    ext = 'destinations'

    driver = SgSelenium().chrome()
    driver.get(locator_domain + ext)

    main = driver.find_element_by_css_selector('main#main-content')
    us_locs = main.find_element_by_css_selector('div.location-listing__column--left')
    hrefs = us_locs.find_elements_by_css_selector('a')

    link_list = []
    for href in hrefs:
        link_list.append(href.get_attribute('href'))

    all_store_data = []
    for link in link_list:
        driver.get(link)
        driver.implicitly_wait(10)

        location_name = driver.find_element_by_css_selector('div.footer-primary__name').text
        phone_number = driver.find_element_by_css_selector('div.footer-primary__number').text
        street_address = driver.find_element_by_css_selector('span.thoroughfare').text
        city = driver.find_element_by_css_selector('span.locality').text
        state = driver.find_element_by_css_selector('span.state').text
        zip_code = driver.find_element_by_css_selector('span.postal-code').text

        country_code = 'US'
        store_number = '<MISSING>'
        location_type = '<MISSING>'

        map_div = driver.find_elements_by_css_selector('div.property-teaser-map')
        if len(map_div) == 1:
            lat = map_div[0].get_attribute('data-lat')
            longit = map_div[0].get_attribute('data-lng')
        else:
            lat = '<MISSING>'
            longit = '<MISSING>'

        hours = '<MISSING>'

        store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code,
                      store_number, phone_number, location_type, lat, longit, hours]

        all_store_data.append(store_data)

    driver.quit()
    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
