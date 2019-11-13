import csv
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
import time


def get_driver():
    options = Options()
    #options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--window-size=1920,1080')
    return webdriver.Chrome('chromedriver', options=options)


def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", 'page_url'])
        # Body
        for row in data:
            writer.writerow(row)


def addy_ext(addy):
    address = addy.split(',')
    city = address[0]
    state_zip = address[1].strip().split(' ')
    state = state_zip[0]
    zip_code = state_zip[1]
    return city, state, zip_code



def fetch_data():
    locator_domain = 'https://www.cometcleaners.com/'
    ext = 'comet-cleaners-locations/'

    driver = get_driver()
    driver.get(locator_domain + ext)

    scrollHeight = driver.execute_script("return document.body.scrollHeight")

    for i in range(0, scrollHeight, 100):
        # Scroll down to bottom
        driver.execute_script("window.scrollTo(0, " + str(i) + ");")
        time.sleep(0.2)

    main = driver.find_element_by_css_selector('div#main-content')

    locs = main.find_elements_by_css_selector('div.wpb_content_element')
    link_store_data = []
    for loc in locs:
        link = loc.find_elements_by_css_selector('a')[1].get_attribute('href')

        cont = loc.text.split('\n')
        if 'COMET CLEANERS' not in cont[0]:
            continue
        if 'MONCLOVA' in cont[0]:
            break

        location_name = cont[0]
        street_address = cont[1]
        city, state, zip_code = addy_ext(cont[2])
        phone_number = cont[3]
        if "THAT'S MY COMET CLEANERS!" in phone_number:
            phone_number = '<MISSING>'

        country_code = 'US'
        location_type = '<MISSING>'
        store_number = '<MISSING>'
        hours = '<MISSING>'
        longit = '<MISSING>'
        lat = '<MISSING>'

        store_data = [link, [locator_domain, location_name, street_address, city, state, zip_code, country_code,
                      store_number, phone_number, location_type, lat, longit, hours]]
        link_store_data.append(store_data)

    all_store_data = []

    for data in link_store_data:
        driver.get(data[0])
        driver.implicitly_wait(10)

        try:
            google_src = driver.find_element_by_xpath("//iframe[contains(@src, 'www.google.com/maps/')]").get_attribute('src')

        except NoSuchElementException:
            all_store_data.append(data[1])
            continue


        start = google_src.find('!2d')
        if start > 0:
            end = google_src.find('!2m')
            coords = google_src[start + 3: end].split('!3d')

            # lat
            data[1][-3] = coords[1]
            # longit
            data[1][-2] = coords[0]

        # link
        data[1][-1] = data[0]
        all_store_data.append(data[1])

        time.sleep(1)

    driver.quit()
    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
