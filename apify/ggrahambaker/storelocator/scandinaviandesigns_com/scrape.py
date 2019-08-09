import csv
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


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


def addy_extractor(src):
    arr = src.split(',')
    city = arr[0]
    state = arr[1].strip()
    zip_code = '<MISSING>'

    return city, state, zip_code


def fetch_data():
    # Your scraper here
    locator_domain = 'https://scandinaviandesigns.com/'
    ext = 'pages/find-a-store'

    driver = get_driver()
    driver.get(locator_domain + ext)

    all_results = driver.find_element_by_css_selector('div#shopify-section-find-stores')
    result = all_results.find_element_by_css_selector('div.row')

    states = result.find_elements_by_css_selector('div.desktop-12')
    all_store_data = []
    for state in states:
        state_stores = state.find_elements_by_css_selector('div.has-store-profile')
        for store in state_stores:
            content = store.text.split('\n')

            if len(content) > 5:
                location_name = '<MISSING>'
                if len(content) == 11:
                    if '12801 North Tatum Blvd' in content[1]:
                        street_address = '12801 North Tatum Blvd'
                        city = 'Phoenix'
                        state = 'AZ'
                        zip_code = '85032'
                    elif '4460 Ontario Mills Parkway Ontario' in content[1]:
                        street_address = '4460 Ontario Mills Parkway Ontario'
                        city = 'Ontario'
                        state = 'CA'
                        zip_code = '91764'
                    elif '865 Blossom Hill Rd' in content[1]:
                        street_address = '865 Blossom Hill Rd'
                        city = 'San Jose'
                        state = 'CA'
                        zip_code = '95123'
                    else:
                        street_address = content[1]
                        # city, state, zip_code = addy_extractor(content[2])
                    hour_off = -1

                    phone_number = content[2]


                else:
                    if '2509 S. Broadway Avenue' in content[1]:
                        street_address = '2509 S. Broadway Avenue'
                        city = 'Boise'
                        state = 'ID'
                        zip_code = '83706'
                    elif '4401 West Empire Place' in content[1]:
                        street_address = '4401 West Empire Place'
                        city = 'Sioux Falls'
                        state = 'SD'
                        zip_code = '57106'
                    elif '16995 NW Cornell Rd' in content[1]:
                        street_address = content[1]
                        city = 'Beaverton'
                        state = 'OR'
                        zip_code = '<MISSING>'

                    else:
                        street_address = content[1]
                        city, state, zip_code = addy_extractor(content[2])

                    if len(content) == 12:
                        hour_off = 0
                    elif len(content) == 13:
                        hour_off = 1
                    if 'Store' in content[3]:
                        phone_number = content[2]
                    else:
                        phone_number = content[3]

                hours = ''
                for h in content[4 + hour_off:-1]:
                    hours += h + ' '

                country_code = 'US'
                location_type = '<MISSING>'
                lat = '<MISSING>'
                longit = '<MISSING>'
                store_number = '<MISSING>'

                store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code,
                              store_number, phone_number, location_type, lat, longit, hours]
                all_store_data.append(store_data)

    driver.quit()
    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
