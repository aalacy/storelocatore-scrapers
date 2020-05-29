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

def addy_extractor(src):
    arr = src.split(',')
    city = arr[0]
    prov_zip = arr[1].strip().split(' ')
    state = prov_zip[0].strip()
    zip_code = prov_zip[1].strip()

    return city, state, zip_code

def fetch_data():
    # Your scraper here
    locator_domain = 'http://bellagiospizza.com/'
    ext = 'locations'

    driver = SgSelenium().chrome()
    driver.implicitly_wait(10)
    driver.get(locator_domain + ext)

    divs = driver.find_elements_by_css_selector('div.gridTitle')

    href_arr = []
    for div in divs:
        href_arr.append(div.find_element_by_css_selector('a').get_attribute('href'))

    all_store_data = []
    for link in href_arr:
        driver.implicitly_wait(10)
        driver.get(link)

        content = driver.find_elements_by_css_selector('div.inner.center.twoPad')[1].text.split('\n')
        cleaned = []
        for con in content:
            if con != '':
                cleaned.append(con)
        location_name = '<MISSING>'
        phone_number = cleaned[2]
        street_address = cleaned[4]
        city, state, zip_code = addy_extractor(cleaned[5])

        hours_arr = driver.find_elements_by_css_selector('div.inner.center.twoPad')[2].text.split('\n')

        hours = ''
        for h in hours_arr:
            hours += h + ' '

        hours = hours.replace('Store Hours', '').strip()

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
