import csv
import os
from sgselenium import SgSelenium
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('thepizzapress_com')



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
    if len(prov_zip) == 3:
        state = prov_zip[0] + ' ' + prov_zip[1]
        zip_code = prov_zip[2]
    else:
        state = prov_zip[0].strip()
        zip_code = prov_zip[1].strip()

    return city, state, zip_code

def fetch_data():
    locator_domain = 'https://www.thepizzapress.com/'
    ext = 'locations/'

    driver = SgSelenium().chrome()
    driver.get(locator_domain + ext)
    locations = driver.find_element_by_css_selector('div.editor-content')

    links = locations.find_elements_by_css_selector('a')

    link_list = []
    for link in links:
        link_list.append(link.get_attribute('href'))

    all_store_data = []
    for link in link_list:
        driver.implicitly_wait(10)
        driver.get(link)
        logger.info('--top--')
        logger.info(driver.find_element_by_css_selector('section.company-info').text.split('\n'))
        details = driver.find_element_by_css_selector('section.company-info').text.split('\n')
        if 'WEST HOLLYWOOD' in details[0]:
            location_name = details[0]
            street_address = details[1] + ' ' + details[2]
            city, state, zip_code = addy_extractor(details[3])
            phone_number = details[5].replace('P:', '').strip()
            hours = ''
            for h in details[7:]:
                hours += h + ' '
        elif 'SACRAMENTO' in details[0]:
            location_name = details[0]
            street_address = details[1]
            city, state, zip_code = addy_extractor(details[2])
            phone_number = '<MISSING>'
            hours = ''
            for h in details[5:]:
                hours += h + ' '

        elif 'THE PIZZA PRESS' in details[0]:
            location_name = details[0]
            street_address = details[1]
            city, state, zip_code = addy_extractor(details[2])
            phone_number = details[4].replace('P:', '').strip()
            hours = ''
            for h in details[6:]:
                hours += h + ' '

        else:
            location_name = '<MISSING>'
            street_address = details[0]
            city, state, zip_code = addy_extractor(details[1])
            phone_number = details[3].replace('P:', '').strip()
            hours = ''
            for h in details[5:]:
                hours += h + ' '

        hours = hours.strip()
        country_code = 'US'
        location_type = '<MISSING>'
        lat = '<MISSING>'
        longit = '<MISSING>'
        store_number = '<MISSING>'

        store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code,
                      store_number, phone_number, location_type, lat, longit, hours]
        logger.info(store_data)

        logger.info('--bottom--')
        all_store_data.append(store_data)

    driver.quit()
    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
