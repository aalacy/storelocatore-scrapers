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


def addy_ext(addy):
    address = addy.split(',')
    city = address[0]
    state_zip = address[1].strip().split(' ')
    state = state_zip[0]
    zip_code = state_zip[1]
    return city, state, zip_code



def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    locator_domain = 'https://www.amerisleep.com/'
    ext = 'retail'

    driver = get_driver()
    driver.get(locator_domain + ext)

    states = driver.find_elements_by_css_selector('div.o-grid__item')
    link_href = []
    for state in states:
        links = state.find_elements_by_css_selector('a')
        for link in links:
            if 'jobs' in link.get_attribute('href'):
                continue
            elif '.html' in link.get_attribute('href'):
                continue
            elif 'baybrook-mall' in link.get_attribute('href'):
                continue
            else:
                link_href.append(link.get_attribute('href'))


    all_store_data = []
    for link in link_href:
        driver.implicitly_wait(10)
        driver.get(link)


        location_name = driver.find_element_by_css_selector('.o-title--bemma').text


        address = driver.find_element_by_css_selector('div.local-page__address').text.split('\n')

        if len(address) == 3:
            street_address = address[0] + ' ' + address[1]
            city, state, zip_code = addy_ext(address[2])
        else:
            if 'SW Washington Square' in address[0]:
                street_address = address[0]
                addy = address[1].split(',')
                city = addy[0]
                state = addy[1].strip()
                zip_code = '<MISSING>'
            else:
                street_address = address[0]
                city, state, zip_code = addy_ext(address[1])

        hours = driver.find_element_by_css_selector('div.o-local-grid__container').text.replace('\n', ' ').strip()
        phone_number = driver.find_element_by_css_selector('div.o-local-grid__item.phone').text

        href = driver.find_element_by_css_selector(
            'p.button-blue--solid.button-small.mb-20').find_element_by_css_selector('a').get_attribute('href')
        start_idx = href.find('/@')
        end_idx = href.find('/data')
        if start_idx > -1:
            coords = href[start_idx + 2:end_idx].split(',')
            lat = coords[0]
            longit = coords[1]
        else:
            lat = '<INACCESSIBLE>'
            longit = '<INACCESSIBLE>'

        country_code = 'US'
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
