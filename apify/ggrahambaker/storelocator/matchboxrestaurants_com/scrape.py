import csv
import os
from sgselenium import SgSelenium
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
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

def check_exists(selector, driver):
    try:
        driver.find_element_by_css_selector(selector)
    except NoSuchElementException:
        return False
    return True

def fetch_data():
    locator_domain = 'https://www.matchboxrestaurants.com/'

    driver = SgSelenium().chrome()
    driver.get(locator_domain)
    driver.implicitly_wait(10)

    if check_exists('a.sqs-popup-overlay-close', driver):
        element = driver.find_element_by_css_selector('a.sqs-popup-overlay-close')
        driver.execute_script("arguments[0].click();", element)

    element_to_hover_over = driver.find_element_by_css_selector("a.Header-nav-folder-title")

    hover = ActionChains(driver).move_to_element(element_to_hover_over)
    hover.perform()

    hrefs = driver.find_element_by_css_selector('span.Header-nav-folder').find_elements_by_css_selector('a')

    link_list = []
    for href in hrefs:
        link_list.append(href.get_attribute('href'))

    all_store_data = []
    for link in link_list:
        if link == 'https://matchboxrestaurants.com/':
            continue
        driver.implicitly_wait(10)
        driver.get(link)
        
        main = driver.find_element_by_css_selector('section.Main-content')
        content = main.text.split('\n')[:17]

        location_name = link[link.find('.com/') + 5: ].replace('-', ' ')
        street_address = content[1]
        city, state, zip_code = addy_ext(content[2])
        phone_number = content[3].replace('call', '').strip()
        hours = ''
        for h in content[11:]:
            if 'order online' in h:
                break
            hours += h + ' '

        if 'ellsworth' in street_address or 'potomac' in street_address:
            href = main.find_elements_by_css_selector('a')[0].get_attribute('href')

        else:
            href = main.find_elements_by_css_selector('a')[1].get_attribute('href')

        start_idx = href.find('/@')
        if start_idx > 0:
            end_idx = href.find('z/data')
            coords = href[start_idx + 2: end_idx].split(',')
            lat = coords[0]
            longit = coords[1]
        else:
            lat = '<MISSING>'
            longit = '<MISSING>'
        country_code = 'US'
        store_number = '<MISSING>'
        location_type = '<MISSING>'

        store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code,
                      store_number, phone_number, location_type, lat, longit, hours, link]
        all_store_data.append(store_data)

    driver.quit()
    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
