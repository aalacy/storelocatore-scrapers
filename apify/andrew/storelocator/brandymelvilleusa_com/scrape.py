import csv
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select
import re

# options = Options() 
# options.add_argument('--headless')
# options.add_argument('--no-sandbox')
# options.add_argument('--disable-dev-shm-usage')
# driver = webdriver.Chrome('/bin/chromedriver', chrome_options=options)
driver = webdriver.Chrome('/usr/local/bin/chromedriver')

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)

def parse_google_url(url):
    if not '@' in url:
        return '<MISSING>', '<MISSING>'
    return re.findall(r'@(-?\d+.{1}\d+,{1}-?\d+.{1}\d+),', url)[0].split(',')

def parse_state_results(state, country_code):
    state_data = []
    stores = driver.find_elements_by_css_selector('div.accordion')
    for store in stores:
        location_name = store.find_element_by_css_selector('div.locations_name > p').text
        city = location_name
        street_address = store.find_element_by_css_selector('div.locations_address > p').text
        phone = store.find_element_by_css_selector('div.locations_number > p').text
        hours_of_operation = store.find_element_by_css_selector('div.show_time').get_attribute('innerHTML')
        google_url = store.find_element_by_css_selector('a').get_attribute('href')
        latitude, longitude = parse_google_url(google_url)
        state_data.append([
            'https://www.brandymelvilleusa.com/',
            location_name,
            street_address,
            city,
            state,
            '<MISSING>',
            country_code,
            '<MISSING>',
            phone,
            '<MISSING>',
            latitude,
            longitude,
            hours_of_operation
        ])
    return state_data

def fetch_data():
    data = []
    driver.get('https://www.brandymelvilleusa.com/locations')
    select_country_el = Select(driver.find_element_by_css_selector(".locations_area"))
    for country, country_code in [('United States', 'US'), ('Canada', 'CA')]:
        select_country_el.select_by_value(country)
        select_state_el = Select(driver.find_element_by_css_selector(".locations_state"))
        states = [
            opt_state.text
            for opt_state in driver.find_elements_by_css_selector('select.locations_state > option')
        ]
        for state in states:
            select_state_el.select_by_value(state)
            data.extend(
                parse_state_results(state, country_code)
            )
    driver.quit()
    return data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
