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

def fetch_data():
    locator_domain = 'https://www.pbteen.com/'
    ext = 'customer-service/store-locator.html?cm_src=OLDLINK&cm_type=fnav'

    driver = get_driver()
    driver.get(locator_domain + ext)
    driver.implicitly_wait(10)

    united_states = driver.find_element_by_css_selector('section#united-states')
    stores = united_states.find_elements_by_css_selector('div.store-card')

    link_list = []
    for store in stores:
        link_list.append(store.find_element_by_css_selector('a').get_attribute('href'))

    all_store_data = []
    for link in link_list:
        driver.get(link)
        driver.implicitly_wait(10)

        location_name = driver.find_element_by_xpath('//h3[@itemprop="name"]').text
        street_address = driver.find_element_by_css_selector('p.storeDetailsAddress').text
        city = driver.find_element_by_xpath('//span[@itemprop="addressLocality"]').text
        state = driver.find_element_by_xpath('//span[@itemprop="addressRegion"]').text
        zip_code = driver.find_element_by_xpath('//span[@itemprop="postalCode"]').text

        phone_number = driver.find_element_by_xpath('//p[@itemprop="telephone"]').text


        div_hours = driver.find_element_by_css_selector('div#storeHours').find_element_by_css_selector('ul')
        hours = div_hours.text.replace('\n', ' ')

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
