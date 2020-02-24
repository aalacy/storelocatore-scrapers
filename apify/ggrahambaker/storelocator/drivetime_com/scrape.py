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
    # Your scraper here
    locator_domain = 'https://www.drivetime.com/'
    ext = 'used-car-dealers'

    driver = get_driver()
    driver.get(locator_domain + ext)
    #element = driver.find_element_by_css_selector('span.right-text')
    #driver.execute_script("arguments[0].click();", element)

    ul = driver.find_element_by_css_selector('ol.link-swamp-list')
    lis = ul.find_elements_by_css_selector('a.inline-link')
    print(len(lis))
    state_list = []
    for li in lis:
        print(li.find_element_by_css_selector('a').get_attribute('href'))
        state_list.append(li.find_element_by_css_selector('a').get_attribute('href'))

    link_list = []
    for state in state_list:
        driver.get(state)
        driver.implicitly_wait(10)
        lis = driver.find_elements_by_css_selector('li.dealership-marker')
        for li in lis:
            link_list.append(li.find_element_by_css_selector('a.dealer-name-link').get_attribute('href'))

    all_store_data = []
    for link in link_list:
        driver.get(link)
        driver.implicitly_wait(10)
        content = driver.find_element_by_css_selector('ul.contact-info').text.split('\n')
        location_name = content[0]
        street_address = content[1]
        city, state, zip_code = addy_ext(content[2])
        phone_number = content[3]
        hours = ''
        for h in content[4:-2]:
            hours += h + ' '

        hours = hours.strip()
        lat = driver.find_element_by_css_selector('a#dealer-directions-link').get_attribute('data-lat')
        longit = driver.find_element_by_css_selector('a#dealer-directions-link').get_attribute('data-long')
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
