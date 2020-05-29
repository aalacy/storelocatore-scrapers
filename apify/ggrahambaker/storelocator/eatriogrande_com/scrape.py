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
    locator_domain = 'http://eatriogrande.com/'
    ext = 'locations/'

    driver = SgSelenium().chrome()
    driver.get(locator_domain + ext)

    driver.find_element_by_xpath("//select[@name='tablepress-2_length']/option[text()='25']").click()
    main = driver.find_element_by_css_selector('tbody')
    stores = main.find_elements_by_css_selector('tr')
    all_store_data = []
    for store in stores:
        cont = store.find_elements_by_css_selector('td')
        city = cont[0].text
        street_address = cont[1].text
        state = cont[3].text
        zip_code = cont[2].text
        phone_number = cont[4].text

        if street_address == '':
            street_address = '<MISSING>'

        lat = '<MISSING>'
        longit = '<MISSING>'

        location_name = '<MISSING>'
        store_number = '<MISSING>'
        location_type = '<MISSING>'

        hours = '<MISSING>'
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
