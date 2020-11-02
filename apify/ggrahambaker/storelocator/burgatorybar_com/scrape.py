import csv
import os
from sgselenium import SgSelenium
import re
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('burgatorybar_com')



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
    prov_zip = arr[1].split(' ')
    if len(prov_zip) == 3:
        state = prov_zip[1].replace('.', '')
        zip_code = prov_zip[2]

    return city, state, zip_code

def scrape_page(driver, locator_domain, location_name, all_store_data):
    driver.get(locator_domain + location_name)
    div = driver.find_element_by_css_selector('div.sqs-block.html-block.sqs-block-html')
    # logger.info(div.get_attribute('innerHTML'))
    addy = div.find_elements_by_css_selector('h2')[0].text.split('\n')
    if len(addy) == 1:
        ## see if there are 2 commas in addy
        comm_split = addy[0].split(',')
        if len(comm_split) == 3:
            street_address = comm_split[0]
            city, state, zip_code = addy_extractor(comm_split[1] + ',' + comm_split[2])

        else:
            addy = addy[0].split(' ')
            street_address = addy[0] + ' ' + addy[1] + ' ' + addy[2]
            city, state, zip_code = addy_extractor(addy[3] + ' ' + addy[4] + ' ' + addy[5])
    else:
        street_address = addy[0]
        city, state, zip_code = addy_extractor(addy[1])

    #logger.info(street_address, city, state, zip_code)

    ps = driver.find_elements_by_css_selector('p')
    hours = ps[0].text.replace('\n', ' ').replace('HOURS:', '').strip()
    phone_number = ps[2].text.strip()
    #logger.info(hours)
    #logger.info(phone_number)
    country_code = 'US'
    store_number = '<MISSING>'
    location_type = '<MISSING>'
    lat = '<MISSING>'
    longit = '<MISSING>'
    all_store_data.append([locator_domain, location_name, street_address, city, state, zip_code, country_code,
                           store_number, phone_number, location_type, lat, longit, hours])

def fetch_data():
    locator_domain = 'https://burgatorybar.com/'

    ext_arr = ['fox-chapel-waterworks', 'robinson-the-pointe', 'homestead-waterfront', 'murrysville-blue-spruce',
               'north-shore', 'mccadless-crossing-north-hills', 'cranberry']

    driver = SgSelenium().chrome()
    all_store_data = []
    for ext in ext_arr:
        scrape_page(driver, locator_domain, ext, all_store_data)

    all_store_data.append([locator_domain, 'ppg-paints-arena', '1001 Fifth Ave', 'Pittsburgh', 'PA', '15219', 'US',
                           '<MISSING>', '<MISSING>', 'stadium', '<MISSING>', '<MISSING>', '<MISSING>'])

    all_store_data.append([locator_domain, 'heinz-field', '100 Art Rooney Ave', 'Pittsburgh', 'PA', '15212', 'US',
                           '<MISSING>', '<MISSING>', 'stadium', '<MISSING>', '<MISSING>', '<MISSING>'])
    driver.quit()
    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
