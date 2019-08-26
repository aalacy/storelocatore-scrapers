import csv
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


def get_driver():
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--window-size=1920,1080')
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


def clean(arr):
    to_ret = []
    for a in arr:
        if 'Store Pickup' in a:
            continue
        elif 'View Weekly Ad' in a:
            continue

        to_ret.append(a)

    return to_ret


def fetch_data():
    locator_domain = 'https://www.amigosunited.com/'
    ext = 'rs/StoreLocator'

    driver = get_driver()
    driver.get(locator_domain + ext)
    driver.implicitly_wait(30)

    locs = driver.find_elements_by_css_selector('div.storeresult-listitem')
    all_store_data = []
    for loc in locs:
        content = clean(loc.text.split('\n'))

        location_type = content[0]
        street_address = content[1]
        city, state, zip_code = addy_ext(content[2])

        phone_number = content[3].replace('Phone:', '').strip()

        hours = ''
        hours_on = False
        for h in content[4:]:
            if 'Pharmacy Phone' in h:
                break
            if 'Store Hours' in h:
                hours_on = True

            if hours_on:
                hours += h + ' '

        lat = '<MISSING>'
        longit = '<MISSING>'
        country_code = 'US'
        store_number = '<MISSING>'
        location_name = '<MISSING>'
        store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code,
                      store_number, phone_number, location_type, lat, longit, hours]
        all_store_data.append(store_data)


    driver.quit()
    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
