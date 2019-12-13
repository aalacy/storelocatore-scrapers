import csv
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import re

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
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def addy_ext(addy):
    address = addy.split(',')
    city = address[0]
    state_zip = address[1].strip().split(' ')
    if len(state_zip) == 3:
        state = state_zip[0] + ' ' + state_zip[1]
        zip_code = state_zip[2]
    else:
        state = state_zip[0]
        zip_code = state_zip[1]
    return city, state, zip_code


def fetch_data():
    locator_domain = 'https://5starnutritionusa.com/'
    ext = 'pages/store-locator'

    driver = get_driver()
    driver.get(locator_domain + ext)

    lis = driver.find_elements_by_css_selector('li.stockist-list-result')

    all_store_data = []
    for li in lis:
        details = li.text.split('\n')
        location_name = details[0]
        street_address = details[1]
        

        if 'Nutrition Blacksburg' in location_name or 'Hattiesburg' in location_name or 'Texarkana' in location_name or 'Braunfels' in location_name:
            street_address += ' ' + details[2]
            city, state, zip_code = addy_ext(details[3])
            if 'Braunfels' in location_name:
                phone_number = details[4]
            else:
                phone_number = details[5]

        elif 'Tuscaloosa' in location_name:
            addy = details[2].split(',')
            city = addy[0]
            state = addy[1].strip()
            zip_code = '<MISSING>'
            phone_number = details[4]
        elif 'West Monroe' in location_name:
            addy = details[2].split(',')
            city = addy[0]
            state = '<MISSING>'
            zip_code = addy[1].strip()
            phone_number = details[4]
        else:
            city, state, zip_code = addy_ext(details[2])
            if '784-3000' in details[3]:
                phone_number = details[3]
            else:
                phone_number = details[4]


        country_code = 'US'
        store_number = '<MISSING>'
        location_type = '<MISSING>'
        lat = '<MISSING>'
        longit = '<MISSING>'
        hours = ''
        for h in details[-7:]:
            hours += h + ' '

    
        page_url = '<MISSING>'

        store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code,
                      store_number, phone_number, location_type, lat, longit, hours, page_url]
        all_store_data.append(store_data)

    driver.quit()
    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
