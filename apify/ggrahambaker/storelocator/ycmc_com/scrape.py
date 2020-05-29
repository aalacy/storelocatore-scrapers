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
    locator_domain = 'https://www.ycmc.com/'
    ext = 'locator'

    driver = SgSelenium().chrome()
    driver.get(locator_domain + ext)
    driver.implicitly_wait(30)

    pop_up = driver.find_element_by_xpath("//a[@title='Close']")
    driver.execute_script("arguments[0].click();", pop_up)

    divs = driver.find_elements_by_css_selector('div.ycmc_store_detail')

    all_store_data = []
    for div in divs:

        ps = div.find_elements_by_css_selector('p')

        location_name = ps[0].text

        addy = ps[1].text.split('\n')

        street_address = addy[0]
        city, state, zip_code = addy_extractor(addy[1])
        phone_number = addy[2].replace('Phone:', '').strip()

        hour_split = ps[2].text.split('\n')
        hours = hour_split[1] + ' ' + hour_split[2]

        country_code = 'US'
        location_type = '<MISSING>'
        lat = '<MISSING>'
        longit = '<MISSING>'
        store_number = '<MISSING>'

        store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code,
                      store_number, phone_number, location_type, lat, longit, hours]

        all_store_data.append(store_data)

    driver.quit()
    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
