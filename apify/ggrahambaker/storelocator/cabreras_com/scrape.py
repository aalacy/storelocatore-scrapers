import csv
import os
from sgselenium import SgSelenium

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
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
    locator_domain = 'https://www.cabreras.com/'
    ext = 'locations'

    driver = SgSelenium().chrome()
    driver.get(locator_domain + ext)
    driver.implicitly_wait(20)

    hrefs = driver.find_elements_by_css_selector('a.ca1link')
    link_list = []
    for href in hrefs:
        if len(href.get_attribute('href')) > 25:
            link_list.append(href.get_attribute('href'))

    all_store_data = []
    for link in link_list:
        driver.implicitly_wait(10)
        driver.get(link)
       
        contents = driver.find_elements_by_css_selector('h2.font_2')[1:14]

        street_address = contents[1].text
        if 'E Live Oak Ave' in street_address:
            href = contents[0].find_element_by_css_selector('a').get_attribute('href')
            start_idx = href.find('@')
            coords = href[start_idx + 1:].split(',')

            lat = coords[0]
            longit = coords[1]
        else:
            lat = '<MISSING>'
            longit = '<MISSING>'

        city, state, zip_code = addy_ext(contents[2].text)
        location_name = city
        phone_number = contents[4].text

        hours = contents[8].text + ' ' + contents[9].text + ' ' + contents[10].text + ' ' + contents[11].text

        country_code = 'US'
        store_number = '<MISSING>'
        location_type = '<MISSING>'

        store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code,
                      store_number, phone_number, location_type, lat, longit, hours, link]
        all_store_data.append(store_data)

    driver.quit()
    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
