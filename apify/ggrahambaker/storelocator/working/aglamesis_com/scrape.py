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
    locator_domain = 'https://www.aglamesis.com/'
    ext = 'gourmet_chocolatiers/cincinnati_locations_a/255.htm'

    driver = get_driver()
    driver.get(locator_domain + ext)

    main = driver.find_element_by_css_selector('div.locations')
    locs = main.find_elements_by_css_selector('div')
    all_store_data = []
    for i, loc in enumerate(locs):
        content = loc.text.split('\n')
        location_name = content[0]
        street_address = content[1]
        city, state, zip_code = addy_ext(content[2])
        phone_number = content[3]
        hours = ''
        for h in content[5:]:
            hours += h + ' '

        hours = hours.strip()

        link = driver.find_elements_by_xpath("//a[contains(@href, 'google.com/maps?')]")[i].get_attribute('href')
        start_idx = link.find('ll=')
        end_idx = link.find('&sa')

        coords = link[start_idx + 3:end_idx].split(',')
        lat = coords[0]
        longit = coords[1]

        country_code = 'US'
        location_type = '<MISSING>'
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
