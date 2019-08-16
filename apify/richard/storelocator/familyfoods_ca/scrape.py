import csv
import re

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait

COMPANY_URL = 'http://familyfoods.ca/'
CHROME_DRIVER_PATH = './chromedriver'

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


def parse_info(store):
    exception_list = {
        "Daysland AB T0B 1A0": {
            "city": "Daysland",
            "province": "AB"
        },
        "Edmonton AB T6V 1A8": {
            "city": "Edmonton",
            "province": "AB"
        },
        "Trochu Family Foods": {
            "street_address": "P.O. BOX 639",
            "city": "<MISSING>",
            "province": "AB",
            "zip_code": "T0M 2C0",

        },
        "MB R0G 0X0": {
            "city": "Holland",
            "province": "MB"
        },
        "338 MAIN ST. MANITOU, MB  R0G 1GO": {
            "street_address": "338 MAIN ST.",
            "city": "MANITOU",
            "province": "MB"
        }

    }

    store_info_list = [info.strip() for info in store.get_attribute('textContent').split('\n') if info.strip() != '']
    phone_number = '<MISSING>'
    for store_info in store_info_list:
        if "Phone: " in store_info:
            phone_number = store_info.replace('Phone:', '').strip()

    zip_code = store_info_list[2][-7:]
    if store_info_list[0] in exception_list.keys():
        street_address = exception_list[store_info_list[0]]["street_address"]
        city = exception_list[store_info_list[0]]["city"]
        province = exception_list[store_info_list[0]]["province"]
        zip_code = exception_list[store_info_list[0]]["zip_code"]
    else:
        store_list = store.find_element_by_css_selector('div.indent > a').get_attribute('innerHTML').split('<br>')
        street_address = store_list[0]

        if len(store_list) == 2:
            if len(store_list[1].split(',')) == 3:
                # Ideal case
                city = store_list[1].split(',')[0].strip()
                province = store_list[1].split(',')[1].strip()
            elif store_list[1].strip() in exception_list.keys():
                city = exception_list[store_list[1].strip()]["city"]
                province = exception_list[store_list[1].strip()]["province"]
            else:
                city = store_list[1].split(',')[0].strip()
                province = store_list[1].split(',')[1].replace(zip_code, '').strip()
        else:
            if store_list[0] in exception_list.keys():
                street_address = exception_list[store_list[0]]["street_address"]
                city = exception_list[store_list[0]]["city"]
                province = exception_list[store_list[0]]["province"]
            else:
                street_address = '<MISSING>'
                city = store_list[0].split(',')[1]
                province = store_list[0].split(',')[2]

    return street_address, city, province, zip_code, phone_number



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
    data = []

    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(CHROME_DRIVER_PATH, options=options)

    # Fetch ajax
    location_url = 'http://familyfoods.ca/store-locator/'
    driver.get(location_url)

    province_urls = [url.get_attribute('href') for url in driver.find_elements_by_css_selector('ul.sub-menu > li.menu-item.menu-item-type-post_type.menu-item-object-page > a')]

    for url in province_urls:
        driver.get(url)

        # Wait until element appears - 10 secs max
        wait = WebDriverWait(driver, 10)
        wait.until(ec.visibility_of_element_located((By.CSS_SELECTOR, ".locations-holder")))

        stores = driver.find_elements_by_css_selector('div.location-info')
        for store in stores:
            locations_title = store.get_attribute('textContent').split('\n')[1].strip()
            street_address, city, state, zip_code, phone_number = parse_info(store)

            locations_titles.append(locations_title)
            street_addresses.append(street_address)
            cities.append(city)
            states.append(state)
            zip_codes.append(zip_code)
            phone_numbers.append(phone_number)

            # Get coordinates. Not all coordinates are there.
            try:
                coord = re.search('([-+]?)([\d]{1,3})(((\.)(\d+)())),([-+]?)([\d]{1,3})(((\.)(\d+)()))', store.find_element_by_css_selector('div.indent > a').get_attribute('href')).group(0).strip().split(',')
                latitude_list.append(coord[0])
                longitude_list.append(coord[1])
            except:
                latitude_list.append('<MISSING>')
                longitude_list.append('<MISSING>')

    # Store data
    for locations_title, street_address, city, state, zipcode, phone_number, latitude, longitude in zip(locations_titles, street_addresses, cities, states, zip_codes, phone_numbers, latitude_list, longitude_list):
        data.append([
            COMPANY_URL,
            locations_title,
            street_address,
            city,
            state,
            zipcode,
            'CA',
            '<MISSING>',
            phone_number,
            '<MISSING>',
            latitude,
            longitude,
            '<INACCESSIBLE>',
        ])

    driver.quit()
    return data


def scrape():
    data = fetch_data()
    write_output(data)

scrape()