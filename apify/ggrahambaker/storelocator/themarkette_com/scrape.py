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
    locator_domain = 'http://www.themarkette.com/'
    ext = 'Markette/Locations.html'

    driver = SgSelenium().chrome()
    driver.get(locator_domain + ext)

    link_list = []

    a_s = driver.find_elements_by_css_selector('a')
    for a in a_s:
        link = a.get_attribute('href')
        if 'Home' in link:
            continue
        if link not in link_list:
            link_list.append(link)

    all_store_data = []
    for link in link_list:
        driver.get(link)
        driver.implicitly_wait(10)
        main = driver.find_element_by_css_selector('div.graphic_textbox_layout_style_default').text.split('\n')

        location_name = main[0]

        store_number = main[0][main[0].find('#') + 1:]

        street_address = main[1]
        city, state, zip_code = addy_ext(main[2])

        if len(main) == 3:
            phone_number = '<MISSING>'
        else:
            phone_number = main[3]
        if len(phone_number) == 3:
            phone_number = '<MISSING>'

        lat = '<MISSING>'
        longit = '<MISSING>'

        location_type = '<MISSING>'
        country_code = 'US'
        hours = '<MISSING>'

        store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code,
                      store_number, phone_number, location_type, lat, longit, hours]
        all_store_data.append(store_data)

    driver.quit()
    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
