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

def addy_extractor(src):
    arr = src.split(',')
    city = arr[0]
    prov_zip = arr[1].strip().split(' ')
    state = prov_zip[0].strip()
    zip_code = prov_zip[1].strip()

    return city, state, zip_code

def fetch_data():
    locator_domain = 'https://www.blackwalnutcafe.com/'
    ext = 'locations/'

    driver = SgSelenium().chrome()
    driver.get(locator_domain + ext)
    divs = driver.find_elements_by_css_selector('div.trigger')

    href_arr = []
    for div in divs:
        href_arr.append(div.find_element_by_css_selector('a').get_attribute('href'))

    all_store_data = []
    for link in href_arr:
        driver.implicitly_wait(10)
        driver.get(link)
        idx = link.find('-locations/')
        location_name = link[idx + 11: -1].replace('-', ' ')

        location_div = driver.find_element_by_css_selector('div.location')

        details = location_div.text.split('\n')
        street_address = details[1]
        city, state, zip_code = addy_extractor(details[2])
        phone_number = details[3]

        hours_div = driver.find_element_by_css_selector('div.columns.large-offset-1.large-3.medium-4').find_element_by_css_selector('p')
        hours = hours_div.text.replace('\n', ' ').replace('REGULAR HOURS', '').strip()

        country_code = 'US'
        location_type = '<MISSING>'

        lat = driver.find_element_by_xpath('//meta[@itemprop="latitude"]').get_attribute('content')
        longit = driver.find_element_by_xpath('//meta[@itemprop="longitude"]').get_attribute('content')
        store_number = '<MISSING>'

        store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code,
                      store_number, phone_number, location_type, lat, longit, hours]
        all_store_data.append(store_data)

    driver.quit()
    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
