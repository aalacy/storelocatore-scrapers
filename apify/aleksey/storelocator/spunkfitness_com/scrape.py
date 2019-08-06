import csv
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
import re

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)

def parse_extra(text):
    return re.compile(r"(?<!^)\n([A-z\'\s\.]+)\,\s([\sA-z]+)\s([0-9]+)\n(\([0-9]{3}\)\s[0-9]{3}\-[0-9]{4})").split(text.replace('Come visit us at:\n', ''))
def parse_hour(text):
    result = '24' in text
    return result
def parse_geo(url):
    lat_lon = re.findall(r'(?<=@)\S+', url)[0]
    lat = lat_lon.split(',')[0]
    lon = lat_lon.split(',')[1]    
    return lat, lon

def fetch_data():
    data = []
    options = Options() 
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    # options.add_argument("--start-maximized")

    # driver = webdriver.Chrome('/usr/local/bin/chromedriver', chrome_options=options)
    driver = webdriver.Chrome('chromedriver', options=options)
    # driver = webdriver.Chrome('./chromedriver.exe', chrome_options=options)

    driver.get('https://www.spunkfitness.com/memberships/')
    # Fetch store urls from location menu
    store_els = driver.find_elements_by_class_name('cta2-heading-wrap')
    store_hrefs = [store_el.find_element_by_xpath('.//a') for store_el in store_els] 
    store_urls = [store_href.get_attribute('href') for store_href in store_hrefs]
    # Fetch data for each store url
    i = 0
    for store_url in store_urls:
        i = i + 1
        index = (i%2) + 1
        driver.get(store_url)
        # Fetch address/phone elements
        location_name = driver.find_element_by_id('main-title').text
        street_address, city, state, zipcode, phone, none = parse_extra(driver.find_element_by_css_selector('div.editor-content p:nth-of-type('+str(index)+')').text)
        lat, lon = parse_geo(driver.find_element_by_css_selector('div.editor-content p a[target="_blank"]').get_attribute('href'))
        hours_of_operation = '24 hours'
        if(parse_hour(driver.find_element_by_css_selector('div.editor-content h2').text) == False):
            hours_of_operation = driver.find_element_by_css_selector('div.editor-content p:nth-of-type(1)').text.replace("\n", ",")
        data.append([
            'https://www.spunkfitness.com/',
            location_name,
            street_address,
            city,
            state,
            zipcode,
            'US',
            '<MISSING>',
            phone,
            '<MISSING>',
            lat,
            lon,
            hours_of_operation
        ])

    driver.quit()
    return data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
