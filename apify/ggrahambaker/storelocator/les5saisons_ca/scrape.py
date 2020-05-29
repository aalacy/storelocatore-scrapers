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

def fetch_data():
    locator_domain = 'http://les5saisons.ca/'
    ext = 'en/contact.html'

    driver = SgSelenium().chrome()
    driver.get(locator_domain + ext)

    names = driver.find_elements_by_xpath('//span[@itemprop="name"]')
    street_addresses = driver.find_elements_by_xpath('//span[@itemprop="streetAddress"]')
    cities = driver.find_elements_by_xpath('//span[@itemprop="addressLocality"]')
    states = driver.find_elements_by_xpath('//span[@itemprop="addressRegion"]')
    codes = driver.find_elements_by_xpath('//span[@itemprop="postalCode"]')
    phones = driver.find_elements_by_xpath('//span[@itemprop="telephone"]')
    hours_arr = driver.find_elements_by_xpath('//time[@itemprop="openingHours"]')
    all_store_data = []
    for i, loc in enumerate(names):
        location_name = loc.find_element_by_css_selector('img').get_attribute('alt')

        street_address = street_addresses[i].text
        city = cities[i].text
        state = states[i].text.replace('(', '').replace(')', '')
        if i == 1:
            zip_code = states[2].text
        else:
            zip_code = codes[i].text
        phone_number = phones[i].text
        hours = hours_arr[i].text

        country_code = 'CA'

        location_type = '<MISSING>'
        page_url = '<MISSING>'
        longit = '<MISSING>'
        lat = '<MISSING>'
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
