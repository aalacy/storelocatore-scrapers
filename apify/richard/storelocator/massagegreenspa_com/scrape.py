import csv

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait

COMPANY_URL = 'https://massagegreenspa.com'
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

def parse_info(address):
    address = address.split(',')
    exception_dict = {
        '542 Westport Ave Norwalk': {
            'street': '542 Westport Ave',
            'city': 'Norwalk',
            'state': 'CT',
            'zip_code': '06851'
        },
        '15829 Pines Blvd Pembroke Pines': {
            'street': '15829 Pines Blvd',
            'city': 'Pembroke Pines',
            'state': 'FL',
            'zip_code': '33028'
        },
        '21227 S Ellsworth Loop #103 Queen Creek': {
            'street': '21227 S Ellsworth Loop #103',
            'city': 'Queen Creek',
            'state': 'AZ',
            'zip_code': '85142'
        },
        '2355 Vanderbilt Beach Rd #190 Naples FL 34109': {
            'street': '2355 Vanderbilt Beach Rd #190',
            'city': 'Naples',
            'state': 'FL',
            'zip_code': '34109'
        },
        '3425 Thomasville Rd #20': {
            'street': '3425 Thomasville Rd #20',
            'city': 'Tallahassee',
            'state': 'FL',
            'zip_code': '32309'
        },
    }
    if address[0].strip() in exception_dict.keys():
        street_address = exception_dict[address[0].strip()]['street']
        city = exception_dict[address[0].strip()]['city']
        state = exception_dict[address[0].strip()]['state']
        zip_code = exception_dict[address[0].strip()]['zip_code']
    else:
        street_address = address[0].strip()
        city = address[1].strip()
        state = address[2].strip().split(' ')[0].strip()
        zip_code = address[2].strip().split(' ')[1].strip()

    return street_address, city, state, zip_code


def fetch_data():
    # store data
    street_addresses = []
    cities = []
    states = []
    zip_codes = []
    data = []

    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(CHROME_DRIVER_PATH, options=options)

    # Fetch store urls from location menu
    location_url = 'https://massagegreenspa.com/spa-locations/'
    driver.get(location_url)

    # Wait until element appears - 10 secs max
    wait = WebDriverWait(driver, 10)
    wait.until(ec.visibility_of_element_located((By.CSS_SELECTOR, ".sabai-directory-listings-with-map-listings.sabai-col-sm-7")))


    locations_titles = [location_title.get_attribute('title') for location_title in driver.find_elements_by_css_selector('div.sabai-directory-title > a')]
    address_infos = [address.get_attribute('textContent').strip() for address in driver.find_elements_by_css_selector('div.sabai-directory-location')]
    phone_numbers = [phone.get_attribute('textContent').strip() for phone in driver.find_elements_by_css_selector('div.sabai-directory-contact-tel > span.sabai-hidden-xs')]

    for address_info in address_infos:
        street_address, city, state, zip_code = parse_info(address_info)
        street_addresses.append(street_address)
        cities.append(city)
        states.append(state)
        zip_codes.append(zip_code)

    # Store data
    for locations_title, street_address, city, state, zipcode, phone_number in zip(locations_titles, street_addresses, cities, states, zip_codes, phone_numbers):
        if 'coming soon' in locations_title.lower():
            pass
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
                '<MISSING>',
                '<MISSING>',
                '<MISSING>',
            ])

    driver.quit()
    return data


def scrape():
    data = fetch_data()
    write_output(data)

scrape()
