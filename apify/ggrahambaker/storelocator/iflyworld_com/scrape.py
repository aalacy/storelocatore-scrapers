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
    zip_code = state_zip[1]
    return city, state, zip_code

def fetch_data():
    locator_domain = 'https://www.iflyworld.com/'
    ext = 'find-a-tunnel/'

    driver = SgSelenium().chrome()
    driver.get(locator_domain + ext)
    main = driver.find_element_by_css_selector('div.wrap.usa')
    a_tags = main.find_elements_by_css_selector('a.loc')

    link_list = [a_tag.get_attribute('href') for a_tag in a_tags]

    all_store_data = []
    for link in link_list:
        driver.get(link)
        driver.implicitly_wait(30)
        main = driver.find_element_by_css_selector('div.info.col')

        content = main.text.split('\n')

        location_name = content[0]
        phone_number = content[-1]
        info = 'INFO'
        hours = 'HOURS'
        info_idx = content.index(info)
        hours_idx = content.index(hours)

        hours = ''
        for h in content[hours_idx + 1: info_idx]:
            hours += h + ' '

        hours = hours.strip()

        addy = content[info_idx + 1: -2]
        street_address = addy[0]
        city, state, zip_code = addy_ext(addy[1])

        location_name = '<MISSING>'
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
