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
    zip_code = state_zip[2]
    return city, state, zip_code

def fetch_data():
    locator_domain = 'https://www.claros.com/'

    driver = SgSelenium().chrome()
    driver.get(locator_domain)

    hrefs = driver.find_elements_by_xpath("//a[contains(@href, 'contact-')]")
    link_list = []
    for href in hrefs:
        if 'us' not in href.get_attribute('href'):
            link_list.append(href.get_attribute('href'))

    all_store_data = []
    for link in link_list:
        driver.implicitly_wait(10)
        driver.get(link)
        txts = driver.find_elements_by_css_selector('div.txt')
        address = txts[1].text.split('\n')
        street_address = address[0]
        city, state, zip_code = addy_ext(address[1])

        phone_number = txts[3].text.split('\n')[1]
        hours = txts[4].text.replace('\n', ' ')

        lat = '<INACCESSIBLE>'
        longit = '<INACCESSIBLE>'

        country_code = 'US'
        store_number = '<MISSING>'
        location_type = '<MISSING>'
        location_name = city
        store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code,
                      store_number, phone_number, location_type, lat, longit, hours]
        all_store_data.append(store_data)

    driver.quit()
    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
