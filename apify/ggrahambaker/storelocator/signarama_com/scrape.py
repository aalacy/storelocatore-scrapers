import csv
import os
from sgselenium import SgSelenium
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import NoAlertPresentException

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    locator_domain = 'https://www.signarama.com/'
    ext = 'storelocator'

    driver = SgSelenium().chrome()
    driver.get(locator_domain + ext)

    main = driver.find_element_by_css_selector('div.state_stors')
    hrefs = main.find_elements_by_css_selector('a')
    link_list = []
    for href in hrefs:
        link = href.get_attribute('href')
        if 'franchise' in link:
            continue

        link_list.append(link)

    all_store_data = []

    for i, link in enumerate(link_list):
        driver.get(link)
        driver.implicitly_wait(30)

        try:
            alert_obj = driver.switch_to.alert
            alert_obj.accept()
        except NoAlertPresentException:
            nothing = 0

        start_idx = link.find('.com/') + 5

        location_name = link[start_idx:].replace('-', ' ')

        street_address = driver.find_element_by_xpath('//span[@itemprop="streetAddress"]').text
        city = driver.find_element_by_xpath('//span[@itemprop="addressLocality"]').text.replace(',', '').strip()
        state = driver.find_element_by_xpath('//span[@itemprop="addressRegion"]').text
        zip_code = driver.find_element_by_xpath('//span[@itemprop="postalCode"]').text

        if "365 Broad Street, New London" in street_address:
            street_address = '365 Broad Street'

        phone_number = driver.find_element_by_xpath('//span[@itemprop="telephone"]').text
        if phone_number == '':
            phone_number = '<MISSING>'

        if not zip_code.isdigit():
            zip_code = '<MISSING>'
        try:
            href = driver.find_element_by_xpath("//a[contains(@href, 'google.com/maps/')]").get_attribute('href')
            start_idx = href.find('/@')
            end_idx = href.find('z/data')

            coords = href[start_idx + 2: end_idx].split(',')
            lat = coords[0]
            longit = coords[1]

        except NoSuchElementException:
            lat = '<MISSING>'
            longit = '<MISSING>'

        hours = '<MISSING>'
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
