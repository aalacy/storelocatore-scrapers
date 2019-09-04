import csv
import re

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait

COMPANY_URL = 'https://team-rehab.com/'
CHROME_DRIVER_PATH = 'chromedriver'

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow([
            "locator_domain",
            "location_name",
            "street_address",
            "city",
            "state",
            "zip",
            "country_code",
            "store_number",
            "phone",
            "location_type",
            "latitude",
            "longitude",
            "hours_of_operation"
        ])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    # store data
    locations_titles = []
    street_addresses = []
    cities = []
    states = []
    zip_codes = []
    latitude_list = []
    longitude_list = []
    phone_numbers = []
    hours = []
    data = []

    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(CHROME_DRIVER_PATH, options=options)

    # Fetch store urls from location menu
    location_url = 'https://team-rehab.com/locations/'
    driver.get(location_url)
    source_str = driver.page_source

    states_url = [re.search('<a href="/locations/[a-zA-Z]+', line).group(0).replace('<a href="/locations/', 'https://team-rehab.com/locations/') for line in source_str.split('\n') if re.search('<a href="/locations/[a-zA-Z]+', line)]
    locations_url = []

    for url in states_url:
        # Navigate to each state url
        driver.get(url)

        # get listings
        locations_titles.extend([title.text for title in driver.find_elements_by_css_selector('div.location__title')])
        street_addresses.extend([address.text.split('\n')[0].strip() for address in driver.find_elements_by_css_selector('div.location__addr')])
        cities.extend([address.text.split('\n')[1].split(',')[0] for address in driver.find_elements_by_css_selector('div.location__addr')])
        states.extend([address.text.split('\n')[1].split(',')[1].strip().split(' ')[0] for address in driver.find_elements_by_css_selector('div.location__addr')])
        zip_codes.extend([address.text.split('\n')[1].split(',')[1].strip().split(' ')[1] for address in driver.find_elements_by_css_selector('div.location__addr')])
        phone_numbers.extend([phone.get_attribute('textContent').replace('Phone:', '').strip() for phone in driver.find_elements_by_css_selector('div.numbers__container > div.col-md-6.location__phone:nth-of-type(1)')])

        # Get individual location url to get hours
        for location_url in driver.find_elements_by_css_selector('div.location__buttons > div.col-md-6 > a.btn.btn-block.btn-secondary'):
            locations_url.append(location_url.get_attribute('href'))

    for location_url in locations_url:
        # Navigate to page
        driver.get(location_url)

        # Wait till the page loads -- it fails when the store is coming soon -- hence try except makes sense here.
        try:
            wait = WebDriverWait(driver, 5)
            wait.until(ec.visibility_of_element_located((By.CSS_SELECTOR, ".hours__desktop")))
            hour = driver.find_element_by_css_selector('div.hours__desktop > table.table > tbody > tr').get_attribute('textContent')
            hours.append(' '.join([
                'Monday: ', hour[0].strip() + '\n',
                'Tuesday: ', hour[1].strip() + '\n',
                'Wednesday: ', hour[2].strip() + '\n',
                'Thursday: ', hour[3].strip() + '\n',
                'Friday: ', hour[4].strip() + '\n',
                'Saturday: ', hour[5].strip() + '\n',
                'Sunday: ', hour[6].strip(),
                            ]))
            source_str = driver.find_element_by_css_selector('div.col-md-6.location__map > div.tab-content > div.tab-pane.active > script').get_attribute('innerHTML').split('\n')
            lat_long = []
            for str in source_str:
                if re.search('([-+]?)([\d]{1,3})(((\.)(\d+)()))', str):
                    lat_long.append(re.search('([-+]?)([\d]{1,3})(((\.)(\d+)()))', str).group(0))

            latitude_list.append(lat_long[0])
            longitude_list.append(lat_long[1])
        except:
            hours.append('<MISSING>')
            latitude_list.append('<MISSING>')
            longitude_list.append('<MISSING>')

    # Store data
    for locations_title, street_address, city, state, zipcode, phone_number, latitude, longitude, hour in zip(locations_titles, street_addresses, cities, states, zip_codes, phone_numbers, latitude_list, longitude_list, hours):
        if 'coming soon' in locations_title.lower():
            continue
        else:
            data.append([
                COMPANY_URL,
                locations_title,
                street_address,
                city,
                state,
                zipcode,
                'US',
                '<MISSING>',
                phone_number,
                '<MISSING>',
                latitude,
                longitude,
                hour,
            ])

    driver.quit()
    return data


def scrape():
    data = fetch_data()
    write_output(data)

scrape()