import csv
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException



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
    locator_domain = 'https://www.massageheights.com/'
    ext = 'locations/'

    driver = get_driver()
    driver.get(locator_domain + ext)
    main = driver.find_element_by_css_selector('div.results-list.auto')
    locs = main.find_elements_by_css_selector('a.site-link.path')
    link_list = []
    for loc in locs:
        link_list.append(loc.get_attribute('href'))

    all_store_data = []
    for i, link in enumerate(link_list):
        driver.get(link)
        driver.implicitly_wait(10)

        try:
            footer = driver.find_element_by_css_selector('section#LocalFooter')
        except NoSuchElementException:
            print('no loc')
            continue

        location_name = driver.find_element_by_css_selector('div.hero-bottom').find_element_by_css_selector(
            'strong').text

        addy = driver.find_element_by_css_selector('div.hero-address').text.replace('Address', '')

        addy_list = addy.split('\n')[1:3]

        street_address = addy_list[0]
        city, state, zip_code = addy_ext(addy_list[1])


        lat = footer.find_element_by_xpath('//meta[@itemprop="latitude"]').get_attribute('content')
        longit = footer.find_element_by_xpath('//meta[@itemprop="longitude"]').get_attribute('content')

        phone_number = driver.find_element_by_css_selector('a.phone').get_attribute('href').replace('tel:', '')

        hours = driver.find_element_by_css_selector('div.hero-hours').text.replace('Hours', '').replace('\n', ' ')

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
