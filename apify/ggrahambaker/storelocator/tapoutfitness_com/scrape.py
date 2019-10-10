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


def fetch_data():
    locator_domain = 'http://tapoutfitness.com/'
    ext = 'locations/'

    driver = get_driver()
    driver.get(locator_domain + ext)

    main = driver.find_element_by_css_selector('div.location_wrapper')

    hrefs = main.find_elements_by_css_selector('a.icon-monitor')

    link_list = []
    for h in hrefs:
        link = h.get_attribute('href')

        if 'dhaka' in link:
            continue
        if 'facebook' in link:
            continue
        if '.mx' in link:
            continue

        link_list.append(link)

    all_store_data = []
    for link in link_list:
        driver.get(link)
        driver.implicitly_wait(10)
        cont = driver.find_element_by_css_selector('p.medium').text.split('\n')

        start_idx = link.find('//')
        end_idx = link.find('.')
        location_name = link[start_idx + 2: end_idx]

        street_address = cont[0]
        city, state, zip_code = addy_ext(cont[1])
        hours = ''
        for h in cont[2:]:
            hours += h + ' '

        hours = hours.strip()

        if hours == '':
            hours = '<MISSING>'


        phone_number = driver.find_element_by_css_selector('a.phone-number').text

        lat = '<MISSING>'
        longit = '<MISSING>'
        location_type = '<MISSING>'
        store_number = '<MISSING>'
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
