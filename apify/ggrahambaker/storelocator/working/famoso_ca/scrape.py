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
    locator_domain = 'https://famoso.ca/'
    ext = 'locations/'

    driver = get_driver()
    driver.get(locator_domain + ext)
    driver.implicitly_wait(10)

    prov_selects = driver.find_element_by_css_selector('ul.provSelect')
    provs = prov_selects.find_elements_by_css_selector('li')
    prov_list = []
    for prov in provs:
        link = prov.find_element_by_css_selector('a').get_attribute('href')
        prov_list.append(link)

    link_list = []
    for prov in prov_list:
        driver.get(prov)
        driver.implicitly_wait(10)
        main = driver.find_element_by_css_selector('ul.locations')
        links = main.find_elements_by_css_selector('a.highlighted')
        for link in links:
            print(link.get_attribute('href'))
            link_list.append(link.get_attribute('href'))

    for link in link_list:
        print(link)
        driver.get(link)
        driver.implicitly_wait(30)

        coords = driver.find_element_by_id('map_marker')
        lat = coords.get_attribute('data-lat')
        longit = coords.get_attribute('data-lng')
        print(lat, longit)

        phone_number = driver.find_element_by_css_selector('div.location-contacts.phone').find_element_by_css_selector(
            'a').text
        print(phone_number)

        address = driver.find_element_by_css_selector('div.location-contacts.location').text.replace('Get directions\n',
                                                                                                     '').replace(
            'LOCATION\n', '')

        addy = address.split('\n')
        street_address = addy[0]
        city_prov = addy[1].split(' ')
        city = city_prov[0]
        state = city_prov[1]
        zip_code = '<MISSING>'
        print(city, state, street_address)

        hours = driver.find_element_by_css_selector('ul.hours-list').text.replace('\n', ' ')
        print(hours)

        start_idx = link.find('s/')
        location_name = link[start_idx + 2:-1].replace('-', ' ')
        print(location_name)

        country_code = 'CA'
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
