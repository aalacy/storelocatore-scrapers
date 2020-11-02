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
    # Your scraper here
    locator_domain = 'https://www.choicesmarkets.com/'

    driver = SgSelenium().chrome()
    driver.get(locator_domain)
    driver.implicitly_wait(30)

    element = driver.find_element_by_css_selector('span.btn.btn--secondary-lighten.btn__store-location.pull-right')
    driver.execute_script("arguments[0].click();", element)

    menu = driver.find_element_by_css_selector('ul.locations-sub-menu')
    lis = menu.find_elements_by_css_selector('li')

    link_list = []
    for li in lis:
        link_list.append(li.find_element_by_css_selector('a').get_attribute('href'))

    all_store_data = []
    for link in link_list:
        driver.get(link)
        driver.implicitly_wait(10)
        main = driver.find_element_by_css_selector('main.grid__item.one-whole')
        content = main.find_element_by_css_selector('div.store-info').text.split('\n')

        street_address = content[1]
        city_prov = content[2].split(',')
        city = city_prov[0]
        state = city_prov[1].strip()
        zip_code = content[3]
        hours = content[5] + ' ' + content[6] + ' ' + content[7] + ' ' + content[8] + ' ' + content[9]
        hours += ' ' + content[10] + ' ' + content[11]
        phone_number = content[13]

        lat = main.find_element_by_css_selector('section#js-google-map').get_attribute('data-lat')
        longit = main.find_element_by_css_selector('section#js-google-map').get_attribute('data-lng')

        location_name = main.find_element_by_css_selector('h1.article-title').text
        country_code = 'CA'
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
