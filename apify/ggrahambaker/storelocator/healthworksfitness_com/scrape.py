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
    locator_domain = 'https://healthworksfitness.com/'
    ext = 'our-locations/'

    driver = SgSelenium().chrome()
    driver.get(locator_domain + ext)

    divs = driver.find_elements_by_css_selector('div.work-info')
    link_list = [div.find_element_by_css_selector('a').get_attribute('href') for div in divs]

    all_store_data = []
    for link in link_list:
        driver.get(link)
        driver.implicitly_wait(10)
        main = driver.find_elements_by_css_selector('div.wpb_text_column.wpb_content_element')[2]
        content = main.text.split('\n')

        if len(content) == 16:
            content = content[:-7]
        if len(content) == 15:
            content = content[:-1]

        addy = content[0].split(',')
        street_address = addy[0]
        city = addy[1].strip()
        state_zip = addy[2].strip().split(' ')
        state = state_zip[0]
        zip_code = state_zip[1]
        hours = ''
        for h in content[1:]:
            hours += h + ' '

        coord = driver.find_element_by_css_selector('div.nectar-google-map')
        lat = coord.get_attribute('data-center-lat')
        longit = coord.get_attribute('data-center-lng')
        location_name = driver.find_elements_by_css_selector('div.wpb_text_column.wpb_content_element')[0].text

        phone = driver.find_elements_by_css_selector('div.wpb_text_column.wpb_content_element')[4].text.split('\n')

        phone_number = phone[1].replace('Telephone:', '').strip()
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
