import csv
import os
from sgselenium import SgSelenium
import json

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation",
                         "page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    locator_domain = 'https://www.wyndhamhotels.com/'
    ext = 'wyndham-garden/locations'

    driver = SgSelenium().chrome()
    driver.get(locator_domain + ext)

    main = driver.find_element_by_css_selector('div.aem-rendered-content')
    hrefs = main.find_elements_by_xpath("//a[contains(@href, '/overview')]")
    link_list = []
    for h in hrefs:
        link = h.get_attribute('href')
        if 'mexico' in link:
            break

        link_list.append(link)

    all_store_data = []
    for link in link_list:
        driver.get(link)
        driver.implicitly_wait(30)
        loc_j = driver.find_element_by_xpath('//script[@type="application/ld+json"]')
        loc_json = json.loads(loc_j.get_attribute('innerHTML'))

        lat = loc_json['geo']['latitude']
        longit = loc_json['geo']['longitude']

        location_name = loc_json['name']
        zip_code = loc_json['address']['postalCode']

        city = loc_json['address']['addressLocality']

        street_address = loc_json['address']['streetAddress']

        state = loc_json['address']['addressRegion']

        country_name = loc_json['address']['addressCountry']
        if 'United States' in country_name:
            country_code = 'US'
        else:
            country_code = 'CA'

        phone_number = loc_json['telephone']

        page_url = link
        location_type = '<MISSING>'
        store_number = '<MISSING>'
        hours = '<MISSING>'

        store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code,
                      store_number, phone_number, location_type, lat, longit, hours, page_url]

        all_store_data.append(store_data)

    driver.quit()
    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
