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

def fetch_data():
    locator_domain = 'https://www.spinpizza.com/'
    ext = 'locations/'

    driver = get_driver()
    driver.get(locator_domain + ext)

    # close popup
    pop_up = driver.find_element_by_css_selector('a.ppsPopupClose.ppsPopupClose_close-black-in-white-circle')
    driver.execute_script("arguments[0].click();", pop_up)

    all_store_data = []

    loc = driver.find_element_by_css_selector('div.locations')
    locations = loc.find_elements_by_css_selector('div.location')
    for location in locations:
        content = location.text.split('\n')
        if len(content) == 11:
            location_name = content[0]
            street_address = content[1]
            addy = content[2].split(',')
            city = addy[0]
            state = addy[1].strip()
            zip_code = content[3]
            phone_number = content[4]
            hours = content[6] + ' ' + content[7]
        elif len(content) == 10:
            if 'Coming Soon' in content[0]:
                continue
        elif len(content) == 12:
            location_name = content[0]
            street_address = content[1] + ' ' + content[2]
            addy = content[3].split(',')
            city = addy[0]
            state = addy[1].strip()
            zip_code = content[4]
            phone_number = content[5]
            hours = content[7] + ' ' + content[8]
        elif len(content) == 14:
            location_name = content[0]
            street_address = content[1] + ' ' + content[2]
            addy = content[3].split(',')
            city = addy[0]
            state = addy[1].strip()
            zip_code = content[4]
            phone_number = content[5]
            hours = content[7] + ' ' + content[8] + ' ' + content[9] + ' ' + content[10]

        country_code = 'US'
        location_type = '<MISSING>'
        lat = '<INACCESSIBLE>'
        longit = '<INACCESSIBLE>'
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
