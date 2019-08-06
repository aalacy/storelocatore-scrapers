import csv
import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException
import re

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)

def parse_extra(address):
    return re.compile(r"(?<!^)\,\s+([A-z0-9\s\-\'\.]+)\,\s+([\s\'A-z]+)\s(?=[0-9]+|[A-z0-9]{3}[\-|\s][A-z0-9]{3})").split(address)

def parse_phone(phone):
    return phone.strip()

def parse_geo(url):
    lat_lon = re.findall(r'(?<=@)\S+', url)
    if lat_lon:
        lat_lon = lat_lon[0].split(',')
        return lat_lon[0], lat_lon[1]
    else:
        return None

def parse_store_num(url):
    length = len(url.split('/'))
    return url.split('/')[length - 1]

def fetch_data():
    data = []
    options = Options() 
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    
    # driver = webdriver.Chrome('/usr/local/bin/chromedriver', chrome_options=options)
    driver = webdriver.Chrome('chromedriver', options=options)
    # driver = webdriver.Chrome('./chromedriver.exe', chrome_options=options)
    country_codes = ['US', 'CA']
    main_urls = ['https://www.solasalonstudios.com/locations', 'https://www.solasalonstudios.ca/locations']
    i = 0
    for main_url in main_urls:
        driver.get(main_url)

        # Fetch store urls from location menu
        store_els = driver.find_elements_by_css_selector('div.link a:nth-of-type(2)')
        store_urls = [store_el.get_attribute('href') for store_el in store_els]

        # Fetch data for each store url
        for store_url in store_urls:
            driver.get(store_url)
            location_name = driver.find_element_by_css_selector('div.location-info h1').text

            # Fetch address/phone elements
            store_number = parse_store_num(driver.current_url)
            try:
                phone = parse_phone(driver.find_element_by_css_selector('div.one-third div.contact-phone-number').text)
            except NoSuchElementException:
                phone = ''
            street_address, city, state, zipcode = parse_extra(driver.find_element_by_css_selector('div.location-info p').text)
            
            map_url = driver.find_element_by_css_selector('div.bs-popover-top a').get_attribute('href')
            if parse_geo(map_url) is None:
                driver.get(map_url)
                WebDriverWait(driver, 5).until(EC.url_contains('/@'))
                lat, lon = parse_geo(driver.current_url)
            else:
                lat, lon = parse_geo(map_url)
            data.append([
                'https://www.solasalonstudios.com',
                location_name,
                street_address,
                city,
                state,
                zipcode,
                country_codes[i],
                store_number,
                phone,
                '<MISSING>',
                lat,
                lon,
                '<MISSING>'
            ])
        i = i + 1
    driver.quit()
    return data

def scrape():
    # fetch_data()
    data = fetch_data()
    write_output(data)

scrape()