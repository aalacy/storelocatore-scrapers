import csv
from sgrequests import SgRequests
import json
import time
from random import randint

from sgselenium import SgSelenium

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url", "operating_info"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    locator_domain = 'https://in-n-out.com/'

    driver = SgSelenium().chrome()
    driver.get('https://locations.in-n-out.com/map2/')

    try:
        element = WebDriverWait(driver, 150).until(EC.presence_of_element_located(
            (By.CLASS_NAME, "icon-search")))
        time.sleep(randint(4,6))
    except:
        print('[!] Error Occured. ')
        print('[?] Check whether system is Online.')

    menu_button = driver.find_element_by_id('search-form').find_element_by_tag_name("button")
    driver.execute_script("arguments[0].click();", menu_button)
    time.sleep(randint(2,4))

    all_store_button = driver.find_element_by_id('menu').find_elements_by_tag_name("button")[2]
    driver.execute_script("arguments[0].click();", all_store_button)
    time.sleep(10)

    store_numbers = []
    page = 1
    while True and page < 200:
        print('Page: ' + str(page))
        results = driver.find_element_by_id('search-results').find_elements_by_tag_name('li')
        for res in results:
            store_number = res.find_element_by_tag_name('img').get_attribute('data-store')
            store_numbers.append(store_number)

        try:
            if not driver.find_element_by_xpath("//button[(@aria-label='Next')]").get_attribute('disabled') == 'true':
                next_button = driver.find_element_by_xpath("//button[(@aria-label='Next')]")
                driver.execute_script("arguments[0].click();", next_button)
                time.sleep(randint(2,4))
            else:
                break
        except:
            break

        page += 1

    print('Done loading pages..')

    api_base = 'https://locations.in-n-out.com/api/finder/get/'
    all_store_data = []
    for store_number in store_numbers:
        try:
            print("Store: " + store_number)
            cont = session.get(api_base + store_number).json()
        except:
            continue

        store_number = cont['StoreNumber']
        location_name = cont['Name']
        # print(location_name)
        street_address = cont['StreetAddress']

        city = cont['City']
        state = cont['State']
        zip_code = cont['ZipCode']
        lat = cont['Latitude']
        longit = cont['Longitude']
        hours = ''
        for day in cont['DiningRoomNormalHours']:
            hours += day['Name'] + ': ' + day['Hours'] + ' '

        location_type = '<MISSING>'
        phone_number = '1-800-786-1000'
        page_url = api_base + str(store_number)
        country_code = 'US'
        dining_hours = cont['DiningRoomHours']
        if not dining_hours:
            dining_hours = '<MISSING>'
        store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code,
                        store_number, phone_number, location_type, lat, longit, hours, page_url, dining_hours]
        all_store_data.append(store_data)
        
    try:
        driver.close()
    except:
        pass

    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
