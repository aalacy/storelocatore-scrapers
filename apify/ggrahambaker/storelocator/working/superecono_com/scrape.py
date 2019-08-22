import csv
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


def get_driver():
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--window-size=1920,1080')
    return webdriver.Chrome('chromedriver', options=options)


def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    locator_domain = 'http://superecono.com/'
    ext = 'index.php?src=directory&view=store'

    driver = get_driver()
    driver.get(locator_domain + ext)
    stores = driver.find_elements_by_css_selector('div.listerItem')
    link_list = []
    for store in stores:
        link_list.append(store.find_element_by_css_selector('a').get_attribute('href'))

    all_store_data = []
    for link in link_list:
        print(link)
        driver.get(link)
        driver.implicitly_wait(10)

        cont = driver.find_element_by_css_selector('div.storeModule').text.split('\n')
        location_name = cont[0]
        start_idx = cont.index('Horario de Operación')
        # print(start_idx)
        content = cont[start_idx:]
        hours = content[2] + ' ' + content[3]
        street_address = content[5]
        city_zip = content[7].split(',')
        city = city_zip[0]
        if city == '':
            city = '<MISSING>'
        zip_code = city_zip[1].strip()
        if zip_code == '':
            zip_code = '<MISSING>'
        if 'PR' in zip_code:
            zip_code = '<MISSING>'
        phone_number = content[-1]
        state = 'PR'

        src = driver.find_elements_by_css_selector('iframe')
        if len(src) == 1:
            src = driver.find_element_by_css_selector('iframe').get_attribute('src')

            print(src)
            start = src.find('!2d')
            end = src.find('!3m2')

            print(src[start + 3: end].split('!3d'))
            if start > 1:
                coords = src[start + 3: end].split('!3d')
                lat = coords[1][:9]
                longit = coords[0][:8]
            else:
                lat = '<MISSING>'
                longit = '<MISSING>'
        else:
            lat = '<MISSING>'
            longit = '<MISSING>'

        location_name = '<MISSING>'
        store_number = '<MISSING>'
        location_type = '<MISSING>'

        hours = '<MISSING>'
        country_code = 'US'

        store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code,
                      store_number, phone_number, location_type, lat, longit, hours]
        all_store_data.append(store_data)

    driver.quit()
    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
