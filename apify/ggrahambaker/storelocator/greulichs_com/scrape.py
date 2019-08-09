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
    prov_zip = arr[1].strip().split(' ')
    state = prov_zip[0].strip()
    zip_code = prov_zip[1].strip()

    return city, state, zip_code



def fetch_data():
    locator_domain = 'https://www.greulichs.com/'
    ext = 'Contact/Find-Us'

    driver = get_driver()
    driver.get(locator_domain + ext)

    all_store_data = []
    for i in range(1, 16):
        div = driver.find_element_by_css_selector('div#loc' + str(i))


        content = div.text.split('\n')

        location_name = content[1]
        street_address = content[3]

        city, state, zip_code = addy_extractor(content[4])
        hours = ''
        for h in content[6:13]:
            hours += h + ' '

        phone_number = content[-4]

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
