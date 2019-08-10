import csv
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import re


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


def addy_extractor(src):
    arr = src.split(',')
    city = arr[0]

    state_zip = arr[1].strip()
    idx = re.search("\d", state_zip)

    state = state_zip[:idx.start()].strip()
    zip_code = state_zip[idx.start():].strip()

    return city, state, zip_code


def addy_extractor_canada(src):
    arr = src.split(',')
    city = arr[0]
    prov_zip = arr[1].strip().split(' ')
    if len(prov_zip) == 4:
        state = prov_zip[0] + ' ' + prov_zip[1]
        zip_code = prov_zip[2] + ' ' + prov_zip[3]
    else:
        state = prov_zip[0]
        zip_code = prov_zip[1] + ' ' + prov_zip[2]

    return city, state, zip_code



def get_hour_idx(arr):
    for i, ele in enumerate(arr):
        if 'Hours' in ele:
            return i + 1


def fetch_data():
    locator_domain = 'https://deciem.com/'
    ext = 'stores'

    driver = get_driver()
    driver.get(locator_domain + ext)

    divs = driver.find_elements_by_css_selector('div.country')
    canada_locs = divs[0]
    us_locs = divs[2]

    c_locs = canada_locs.find_elements_by_css_selector('div.location')
    all_store_data = []
    for loc in c_locs:
        content = loc.text.split('\n')
        if len(content) > 2:
            location_name = content[0]
            street_address = content[1]
            if '130 King Street West' in street_address:
                street_address += ' ' + content[2]
                city, state, zip_code = addy_extractor_canada(content[3])
                phone_number = content[6]
            else:
                city, state, zip_code = addy_extractor_canada(content[2])
                phone_number = content[5]

            hours_idx = get_hour_idx(content)
            hours = ''
            for h in content[hours_idx:]:
                hours += h + ' '

            hours = hours.strip()

            country_code = 'CA'
            store_number = '<MISSING>'
            location_type = '<MISSING>'
            lat = '<MISSING>'
            longit = '<MISSING>'

            store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code,
                          store_number, phone_number, location_type, lat, longit, hours]
            all_store_data.append(store_data)

    u_locs = us_locs.find_elements_by_css_selector('div.location')
    for loc in u_locs:
        content = loc.text.split('\n')
        if len(content) > 2:
            location_name = content[0]
            street_address = content[1]

            city, state, zip_code = addy_extractor(content[2])
            phone_number = content[5]

            hours_idx = get_hour_idx(content)
            hours = ''
            for h in content[hours_idx:]:
                hours += h + ' '

            hours = hours.strip()


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
