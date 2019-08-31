import csv
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
import re

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            if(row[0] != 0):
                writer.writerow(row)

def parse_extra(text):
    street_address = text.split("\n")[1]
    result = re.compile(r"([A-z\s]+)\,\s([A-z]+)\s([0-9]+)").split(text.split("\n")[2])
    return street_address, result[1], result[2], result[3]

def parse_store_number(url):
    return url.split('/')[len(url.split('/')) - 2]

def parse_id(id):
    length = len(id.split('-'))
    return id.split('-')[length - 1]

def fetch_data():
    # data = []
    data = [[0]*13 for i in range(100)]
    options = Options() 
    # options.add_argument('--headless')
    # options.add_argument('--no-sandbox')
    # options.add_argument('--disable-dev-shm-usage')
    options.add_argument("--start-maximized")
    # driver = webdriver.Chrome('/usr/local/bin/chromedriver', chrome_options=options)
    driver = webdriver.Chrome('chromedriver', options=options)
    # driver = webdriver.Chrome('./chromedriver.exe', chrome_options=options)

    driver.get('https://www.peachtreemed.com/location/')
    try:
        WebDriverWait(driver, 3).until(EC.alert_is_present(),"" )
        alert = driver.switch_to.alert
        alert.accept()
    except TimeoutException:
        print('No alert')
    
    stores = driver.find_elements_by_class_name('hospital-list-item')
    i = 0

    for store in stores:
        store_number = parse_id(store.get_attribute('id'))
        store_info = driver.execute_script("return hsp_info[id_index["+store_number+"]]")
        lat, lon = store_info['coords']
        street_address = store_info['address_1']
        state = store_info['state']
        phone = store_info['phone_number']
        location_name = store_info['title']
        zipcode = store_info['zip']
        city = store_info['city']

        data[i][10] = lat
        data[i][11] = lon
        data[i][0] = "https://www.smartcareuc.com/"
        data[i][1] = location_name
        data[i][2] = street_address
        data[i][3] = city
        data[i][4] = state
        data[i][5] = zipcode
        data[i][6] = "US"
        data[i][7] = store_number
        data[i][8] = phone
        data[i][9] = ""

        i += 1

    store_els = driver.find_elements_by_css_selector('div.hospital-list-item h4:nth-of-type(6) a.directions-link')
    # Fetch store urls from location menu
    store_urls = [store_el.get_attribute('href') for store_el in store_els]
    # Fetch data for each store url
    i = 0    
    for store_url in store_urls:
        driver.get(store_url)
        hours_of_operation = driver.find_element_by_css_selector('div.entry-content ul li:nth-of-type(3)').text.replace('HOURS:','')[1:].replace("\n",",")
        data[i][12] = hours_of_operation
        i += 1
    driver.quit()
    return data

def scrape():
    # fetch_data()
    data = fetch_data()
    write_output(data)

scrape()
