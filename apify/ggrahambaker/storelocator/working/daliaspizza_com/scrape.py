import csv
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains

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
    locator_domain = 'https://www.daliaspizza.com/'

    driver = get_driver()
    driver.get(locator_domain)

    element_to_hover_over = driver.find_element_by_css_selector('li#menu-item-90')

    hover = ActionChains(driver).move_to_element(element_to_hover_over)
    hover.perform()

    ul = driver.find_element_by_css_selector('ul.sub-menu')
    lis = ul.find_elements_by_css_selector('li')
    link_list = []
    for li in lis:
        link_list.append(li.find_element_by_css_selector('a').get_attribute('href'))

    all_store_data = []
    for link in link_list:
        driver.implicitly_wait(10)
        driver.get(link)
        body = driver.find_element_by_css_selector('tbody')
        content = body.text.split('\n')

        if len(content) == 5:
            location_name = content[0]
            address = content[1]
            start_idx = address.find('RdR')
            street_address = address[:start_idx + 2]
            rest_address = address[start_idx + 2:].split(',')
            city = rest_address[0]
            state_zip = rest_address[1].split(' ')
            state = state_zip[0][:-1]
            zip_code = state_zip[1]
            phone_number = content[2]
        else:
            location_name = content[0]
            street_address = content[1]
            city, state, zip_code = addy_ext(content[2])
            phone_number = content[3]

        href = driver.find_element_by_xpath("//a[contains(text(),'View Larger Map')]").get_attribute('href')
        start_idx = href.find('ll=')
        end_idx = href.find('&ss')

        coords = href[start_idx + 3:end_idx].split(',')
        lat = coords[0]
        longit = coords[1]

        hours = '<MISSING>'
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
