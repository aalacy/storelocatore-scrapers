import csv
import os
from sgselenium import SgSelenium

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
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
    locator_domain = 'https://www.graeters.com/'
    ext = 'neighborhood-locations'

    driver = SgSelenium().chrome()
    driver.get(locator_domain + ext)

    hrefs = driver.find_elements_by_xpath("//a[contains(@href, 'retail-stores/')]")
    link_list = []
    for href in hrefs:
        link_list.append(href.get_attribute('href'))
    all_store_data = []

    for link in link_list:

        driver.get(link)
        driver.implicitly_wait(10)

        google_link = driver.find_element_by_xpath("//a[contains(@href, 'google.com/maps/dir/')]").get_attribute('href')
        start_idx = google_link.find('Current+Location/') + len('Current+Location/')
        coords = google_link[start_idx:].split(',')

        lat = coords[0]
        longit = coords[1]

        phone_number = driver.find_element_by_xpath("//a[contains(@href, 'tel:')]").get_attribute('href').replace(
            'tel:', '').strip()

        location_name = driver.find_element_by_css_selector(
            'p.oswald-font.medium-text.medium-large-text-mobile.graeters-brown').text

        addy = driver.find_element_by_css_selector('p.georgia-font.medium-small-text.graeters-brown').text.split('\n')

        if "We've Moved!" in addy[0]:
            addy = driver.find_elements_by_css_selector('p.georgia-font.medium-small-text.graeters-brown')[
                1].text.split('\n')
        street_address = addy[0]
        city, state, zip_code = addy_ext(addy[1])

        hours = driver.find_elements_by_css_selector('p.georgia-font.graeters-brown')[2].text.replace('\n', ' ')

        country_code = 'US'
        page_url = link
        store_number = '<MISSING>'
        location_type = '<MISSING>'

        store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code,
                      store_number, phone_number, location_type, lat, longit, hours, page_url]

        all_store_data.append(store_data)

    driver.quit()
    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
