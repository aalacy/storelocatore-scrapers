import csv
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time

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
    addy = addy.replace(',,', ',')
    address = addy.split(',')
    if len(address) == 3:
        city = address[0]
        state = address[1].strip()
        zip_cont = address[2].strip().split(' ')
        zip_code = zip_cont[1] + ' ' + zip_cont[2]
        country_code = 'CA'
    else:
        city = address[0]
        state_zip = address[1].strip().split(' ')
        if len(state_zip) == 3:
            state = state_zip[0] + ' ' + state_zip[1]
            zip_code = state_zip[2]
        else:
            state = state_zip[0]
            zip_code = state_zip[1]
        country_code = 'US'

    return city, state, zip_code, country_code


def peel_info(driver, locator_domain, all_store_data, dup_list):
    main = driver.find_element_by_css_selector('div#map_sidebar')
    locs = main.find_elements_by_css_selector('div.results_entry')

    for loc in locs:
        #print(loc.text.split('\n'))
        content = loc.text.split('\n')
        #print(len(content))
        location_name = '<MISSING>'
        type_arr = content[0].split(' ')
        #print(len(type_arr))
        if len(type_arr) == 6:
            location_type = type_arr[0] + ' ' + type_arr[1] + ' ' + type_arr[4] + ' ' + type_arr[5]
        elif len(type_arr) == 5:
            location_type = type_arr[0] + ' ' + type_arr[3] + ' ' + type_arr[4]
        else:
            location_type = '<MISSING>'

        street_address = content[1]
        if 'Carretera a Nogales' in street_address:
            continue
        if street_address == '0':
            continue
        if street_address in dup_list:
            continue
        dup_list.append(street_address)
        if 'Industrial Paramedic Services' in street_address:
            city = 'Fort St. John'
            state = 'British Columbia'
            zip_code = ' V1A 2J5'
        else:
            city, state, zip_code, country_code = addy_ext(content[2])
        phone_number = content[3]
        if 'Email' in phone_number:
            phone_number = '<MISSING>'

        store_number = '<MISSING>'
        location_type = '<MISSING>'
        lat = '<MISSING>'
        longit = '<MISSING>'
        hours = '<MISSING>'

        store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code,
                         store_number, phone_number, location_type, lat, longit, hours ]
        all_store_data.append(store_data)
        print()


def fetch_data():
    locator_domain = 'https://www.dxpe.com/'
    ext = 'locations/'

    driver = get_driver()
    driver.get(locator_domain + ext)

    zip_array = ['T1R 1C1', '97062', '92807', '77565', '78664', '75662', 'B3B 1L5', 'L8E 3N9', '50401',
                 '44133', '74146', '79602', '32837', '37210', '68850', '80524', '58801', 'T2C 3H2', 'V1A 2J5',
                 '88240', '79336', '46706', '55121', '68127', '66214']


    all_store_data = []
    dup_list = []
    for zip_search in zip_array:
        search_bar = driver.find_element_by_css_selector('input#autocomplete')
        search_bar.clear()
        print(zip_search)
        search_bar.send_keys(zip_search)

        sub = driver.find_element_by_css_selector('input#addressSubmit')
        driver.execute_script("arguments[0].click();", sub)

        driver.implicitly_wait(10)
        time.sleep(4)
        peel_info(driver, locator_domain, all_store_data, dup_list)

    driver.quit()
    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
