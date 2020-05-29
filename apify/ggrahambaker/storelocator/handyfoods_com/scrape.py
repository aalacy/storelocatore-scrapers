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

def fetch_data():
    locator_domain = 'http://handyfoods.com/'
    ext = 'locations.html'

    driver = SgSelenium().chrome()
    driver.get(locator_domain + ext)

    rows = driver.find_element_by_css_selector('tbody').find_elements_by_css_selector('tr')[1:]
    all_store_data = []
    for row in rows:
        cols = row.find_elements_by_css_selector('td')
        if cols[1].text.strip() == '':
            continue

        store_number = cols[0].text

        addy = cols[1].text.split(',')
        if len(addy) == 1:
            addy = cols[1].text.split('.')
        street_address = addy[0]
        city_zip = addy[1].strip().split(' ')
        if len(city_zip) == 3:
            city = city_zip[0] + ' ' + city_zip[1]
            zip_code = city_zip[2]
        else:
            city = city_zip[0]
            zip_code = city_zip[1]
        state = 'FL'

        phone_number = cols[2].text

        location_type = cols[3].text

        country_code = 'US'
        lat = '<MISSING>'
        longit = '<MISSING>'
        location_name = '<MISSING>'
        hours = '<MISSING>'
        page_url = '<MISSING>'

        store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code,
                      store_number, phone_number, location_type, lat, longit, hours, page_url]
        all_store_data.append(store_data)

    driver.quit()
    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
