import csv
import os
from sgselenium import SgSelenium
from selenium.common.exceptions import NoSuchElementException

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
    if len(state_zip) == 1:
        state = state_zip[0]
        zip_code = '<MISSING>'
    else:
        state = state_zip[0]
        zip_code = state_zip[1]
    return city, state, zip_code

def fetch_data():
    locator_domain = 'https://www.silverminesubs.com/'
    ext = 'locations/'

    driver = SgSelenium().chrome()
    driver.get(locator_domain + ext)

    map_div = driver.find_element_by_css_selector('div#map')
    links = map_div.find_elements_by_css_selector('a')
    link_list = []
    for link in links:
        link_list.append(link.get_attribute('href'))

    store_link = []
    for link in link_list:
        driver.get(link)
        driver.implicitly_wait(10)
        stores = driver.find_elements_by_css_selector('div.storename')
        for store in stores:
            link = store.find_element_by_css_selector('a').get_attribute('href')
            if 'madison' in link:
                continue
            if link not in store_link:
                store_link.append(link)

            else:
                continue

    all_store_data = []
    for link in store_link:
        driver.get(link)
        driver.implicitly_wait(10)

        try:
            geo_href = driver.find_element_by_css_selector('iframe').get_attribute('src')

        except NoSuchElementException:
            continue

        start_idx = geo_href.find('&ll')
        if start_idx > 0:
            end_idx = geo_href.find('&spn')
            coords = geo_href[start_idx + 4: end_idx].split(',')
            lat = coords[0]
            longit = coords[1]

        else:
            lat = '<MISSING>'
            longit = '<MISSING>'

        address_div = driver.find_element_by_xpath("//h3[contains(text(),'Address')]").find_element_by_xpath('..')

        addy = address_div.text.split('\n')

        street_address = addy[1]
        if len(addy) == 2:
            city, state, zip_code = '<MISSING>', '<MISSING>', '<MISSING>'
        elif len(addy) == 4:
            street_address += ' ' + addy[2]
            city, state, zip_code = addy_ext(addy[3])
        else:
            city, state, zip_code = addy_ext(addy[2])

        phone_div = driver.find_element_by_xpath("//h3[contains(text(),'Phone')]").find_element_by_xpath('..')
        phone_number = phone_div.text.split('\n')[1]

        hours_div = driver.find_element_by_xpath("//h3[contains(text(),'Hours')]").find_element_by_xpath('..')
        hours_list = hours_div.text.split('\n')
        hours = ''
        for h in hours_list[1:]:
            hours += h + ' '

        hours = hours.strip()

        location_name = '<MISSING>'
        store_number = '<MISSING>'
        location_type = '<MISSING>'
        country_code = 'US'

        store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code,
                      store_number, phone_number, location_type, lat, longit, hours]

        all_store_data.append(store_data)

    driver.quit()
    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
