import csv
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


def get_driver():
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    return webdriver.Chrome('chromedriver', options=options)


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
    locator_domain = 'http://www.vinnysitaliangrill.com/'
    ext = 'locations/'
    seen_garrison = False
    driver = get_driver()
    driver.get(locator_domain + ext)

    cont = driver.find_element_by_css_selector('div.blog-lg-area-left')
    stores = cont.find_elements_by_css_selector('div.div_location')

    all_store_data = []
    for store in stores:
        if seen_garrison:
            continue
        content = store.text.split('\n')
        if len(content) == 5:
            street_address = content[0]
            city, state, zip_code = addy_ext(content[2])
            phone_number = content[3].replace('Phone:', '').strip()
        else:
            street_address = content[0]
            if 'Connor' in street_address:
                city, state, zip_code = '<MISSING>', '<MISSING>', '<MISSING>'
            elif 'Plantation' in street_address:
                city = 'Fredericksburg'
                state = 'VA'
                zip_code = '22406'
            elif 'Tappahannock' in street_address:
                city = 'Fredericksburg'
                state = 'VA'
                zip_code = '22406'
            else:
                city, state, zip_code = addy_ext(content[1])

            phone_number = content[2].replace('Phone:', '').strip()

            country_code = 'US'
            location_name = '<MISSING>'
            store_number = '<MISSING>'
            location_type = '<MISSING>'
            lat = '<MISSING>'
            longit = '<MISSING>'
            hours = '<MISSING>'
            if 'Garrisonville' in street_address:
                seen_garrison = True

            store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code,
                          store_number, phone_number, location_type, lat, longit, hours]
            all_store_data.append(store_data)

    driver.quit()
    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
