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
    zip_code = prov_zip[1]
    if len(zip_code) == 4:
        zip_code = '0' + zip_code

    return city, state, zip_code



def fetch_data():
    locator_domain = 'https://wingsover.com/'
    ext = 'locations/'

    driver = get_driver()
    driver.get(locator_domain + ext)

    to_click = driver.find_elements_by_css_selector('div.name')
    for clicks in to_click:
        if 'CONNECTICUT' in clicks.text:
            continue
        driver.execute_script("arguments[0].click();", clicks)

    names = driver.find_element_by_css_selector('div.locs').find_elements_by_css_selector('p')

    name_arr = []
    for name in names:
        name_arr.append(name.get_attribute('data-link'))

    all_store_data = []
    for name in name_arr:
        driver.get(locator_domain + ext + name)
        driver.implicitly_wait(10)

        section = driver.find_element_by_xpath("//section[@data-location='" + name + "']")

        location_name = section.find_element_by_css_selector('div.title').find_element_by_css_selector('h2').text

        info = section.find_element_by_css_selector('div.copy').text.split('\n')

        street_address = info[0]
        city, state, zip_code = addy_extractor(info[1])
        phone_number = info[2]
        hours = ''
        for h in info[4:]:
            hours += h + ' '
        hours = hours.strip()

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
