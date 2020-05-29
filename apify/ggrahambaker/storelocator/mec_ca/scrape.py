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
    locator_domain = 'https://www.mec.ca/'
    ext = 'en/stores'

    driver = SgSelenium().chrome()
    driver.get(locator_domain + ext)

    stores_container = driver.find_element_by_css_selector('ul.stores-list.stores-list--all')
    store_links = stores_container.find_elements_by_css_selector('a.store__name')

    link_list = []
    for link in store_links:
        link_list.append(link.get_attribute('href'))

    all_store_data = []
    for link in link_list:
        driver.get(link)

        driver.implicitly_wait(10)
        location_name = driver.find_element_by_xpath('//h1[@itemprop="name"]').text
        street_address = driver.find_element_by_xpath('//span[@itemprop="streetAddress"]').text
        city = driver.find_element_by_xpath('//span[@itemprop="addressLocality"]').text
        state = driver.find_element_by_xpath('//span[@itemprop="addressRegion"]').text
        zip_code = driver.find_element_by_xpath('//span[@itemprop="postalCode"]').text
        hours_table = driver.find_element_by_css_selector('table').text.replace('\n', ' ').strip()
        phone_number = driver.find_element_by_xpath('//span[@itemprop="telephone"]').text

        hours = hours_table.replace('Regular hours', '').replace('Hours', '').replace('View holiday closures',
                                                                                      '').strip()
        geo_links = driver.find_element_by_css_selector('li.list__item.u-no-margin').find_elements_by_css_selector('a')
        for geo in geo_links:
            geo_href = geo.get_attribute('href')
            start_idx = geo_href.find('&sll=')
            end_idx = geo_href.find('&gl')

            if start_idx > 0:
                coords = geo_href[start_idx + 5: end_idx].split(',')
                lat = coords[0]
                longit = coords[1]
                if lat == '':
                    lat = '43.769509'
                    longit = ' -79.375179'
                break

        store_number = '<MISSING>'
        location_type = '<MISSING>'
        country_code = 'CA'
        store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code,
                      store_number, phone_number, location_type, lat, longit, hours]

        all_store_data.append(store_data)

    driver.quit()
    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
