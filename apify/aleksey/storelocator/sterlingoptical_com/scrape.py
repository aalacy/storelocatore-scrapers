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

def parse_phone(phone):
    return phone.replace('Phone: ', '')

def parse_geo(url):
    lat_lon = re.findall(r'(?<=@)\S+', url)
    if lat_lon:
        lat_lon = lat_lon[0].split(',')
        return lat_lon[0], lat_lon[1]
    else:
        return None

def parse_store_num(url):
    length = len(url.split('/'))
    return url.split('/')[length - 2]

def fetch_data():
    data = []
    options = Options() 
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    
    # driver = webdriver.Chrome('/usr/local/bin/chromedriver', chrome_options=options)
    driver = webdriver.Chrome('chromedriver', options=options)
    # driver = webdriver.Chrome('./chromedriver.exe', chrome_options=options)
    driver.get('https://www.sterlingoptical.com/locations')
    # Fetch store urls from location menu
    store_els = driver.find_elements_by_css_selector('div.single-location')
    # Fetch data for each store url
    detail_urls = []
    
    for store_el in store_els:
        try:
            is_located = store_el.find_element_by_css_selector('span.is-closed').text
            location_name = store_el.find_element_by_css_selector('h3').text
            street_address = store_el.find_element_by_css_selector('span.street-address').text
            city = store_el.find_element_by_css_selector('span.locality').text
            state = store_el.find_element_by_css_selector('span.region').text
            zipcode = store_el.find_element_by_css_selector('span.postal-code').text
            store_number = parse_store_num(store_el.find_element_by_css_selector('a.single-location-link').get_attribute('href'))
            try:
                phone = parse_phone(store_el.find_element_by_css_selector('a.tel').text)
            except NoSuchElementException:
                phone = ''
            data.append([
                'https://sterlingoptical.com',
                location_name,
                street_address,
                city,
                state,
                zipcode,
                'US',
                store_number, #store_number
                phone,
                '<MISSING>',
                '<MISSING>', #latitude
                '<MISSING>', #longitude
                '<MISSING>'
            ])
        except NoSuchElementException:
            detail_urls.append(store_el.find_element_by_css_selector('a.single-location-link').get_attribute('href'))
            is_located = ''    
    for detail_url in detail_urls:
        driver.get(detail_url)
        location_name = driver.find_element_by_css_selector('a.location-page-link-city').text
        street_address = driver.find_element_by_css_selector('span.street-address').text
        city = driver.find_element_by_css_selector('span.locality').text
        state = driver.find_element_by_css_selector('span.region').text
        zipcode = driver.find_element_by_css_selector('span.postal-code').text
        hours_of_operation = driver.find_element_by_css_selector('ul.store-hours').text.replace("\n", ",")
        store_number = parse_store_num(driver.current_url)
        try:
            phone = parse_phone(driver.find_element_by_css_selector('a.tel').text)
        except NoSuchElementException:
            phone = ''
        map_url = driver.find_element_by_css_selector('a.location-directions-link').get_attribute('href')
        if parse_geo(map_url) is None:
            driver.get(map_url)
            WebDriverWait(driver, 5).until(EC.url_contains('/@'))
            lat, lon = parse_geo(driver.current_url)
        else:
            lat, lon = parse_geo(map_url)
        data.append([
            'https://sterlingoptical.com',
            location_name,
            street_address,
            city,
            state,
            zipcode,
            'US',
            store_number,
            phone,
            '<MISSING>',
            lat,
            lon,
            hours_of_operation
        ])

    driver.quit()
    return data
def scrape():
    # fetch_data()
    data = fetch_data()
    write_output(data)

scrape()