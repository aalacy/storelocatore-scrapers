import csv
import os
from sgselenium import SgSelenium
import re

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    locator_domain = 'https://www.giuseppezanotti.com/'
    ext = 'wo/store-finder/'

    driver = SgSelenium().chrome()
    driver.get(locator_domain + ext)

    driver.implicitly_wait(10)
    driver.find_element_by_css_selector('select#select_country').click()
    driver.find_element_by_xpath("//option[@value='US']").click()

    hrefs = driver.find_elements_by_css_selector('a.store-detail-link')

    links = []
    for href in hrefs:
        links.append(href.get_attribute('href'))

    all_store_data = []
    for link in links:
        driver.implicitly_wait(10)
        driver.get(link)

        store = driver.find_element_by_css_selector('div.store-detail').text.split('\n')

        location_name = store[1]
        address = store[2]

        if 'Las Vegas' in address:
            # '3500 Las Vegas Blvd, Las Vegas, NV 89109 - Las Vegas,'
            addy_split = address.split(' -')
            addy_split2 = addy_split[0].split(',')
            street_address = addy_split2[0]
            city = addy_split2[1]
            addy_split3 = addy_split2[2].strip().split(' ')
            state = addy_split3[0]
            zip_code = addy_split3[1]
        elif 'Bal Harbour Shops' in address:
            # 'Bal Harbour Shops, 9700 Collins avenue - Bal Harbour, Florida ,'
            addy_split = address.split(' - ')
            street_address = addy_split[0].split(',')[1].strip()
            city_state = addy_split[1].split(',')
            city = city_state[0]
            state = city_state[1]
            zip_code = '<MISSING>'
        elif 'Phipps Plaza' in address or 'Millenia' in address or 'Brickell' in address:
            # 'Brickell City Centre, 701 South Miami Avenue - Miami,'
            # 'The Mall at Millenia, 4200 Conroy Rd - Orlando,'
            # 'Phipps Plaza, 3500 Peachtree Road - Atlanta,'
            addy_split = address.split(',')
            addy_split2 = addy_split[1].split(' - ')
            street_address = addy_split2[0]
            city = addy_split2[1]
            state = '<MISSING>'
            zip_code = '<MISSING>'

        elif 'Brighton' in address:
            addy_split = address.split(' ')
            street_address = addy_split[0] + ' ' + addy_split[1] + ' ' + addy_split[2]
            city = addy_split[3] + ' ' + addy_split[4]
            state = addy_split[5]
            zip_code = addy_split[6]
        else:
            # Los Angeles, hills, new york, hourson
            addy_split = address.split(',')
            street_address = addy_split[0]
            addy_split2 = addy_split[1].split(' - ')
            city = addy_split2[1].replace(',', '').strip()

            addy_split3 = addy_split2[0].strip().split(' ')
            state = addy_split3[0]
            zip_code = addy_split3[1]

        phone_number = store[4]

        hours = ''
        for h in store[6:]:
            hours += h + ' '

        hours = hours.strip()

        country_code = 'US'
        store_number = '<MISSING>'
        location_type = '<MISSING>'
        lat = '<MISSING>'
        longit = '<MISSING>'

        store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code,
                      store_number, phone_number, location_type, lat, longit, hours]
        all_store_data.append(store_data)

    driver.quit()
    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
