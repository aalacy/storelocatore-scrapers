import csv
import os
from sgselenium import SgSelenium
import json
import re
import time

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)

def addy_ext(addy):
    address = addy.split(',')
    city = address[0]
    state_zip = address[1].strip().split(' ')
    state = state_zip[0]
    try:
        zip_code = state_zip[1]
    except:
        zip_code = '<MISSING>'
    return city, state, zip_code

def fetch_data():
    locator_domain = 'https://ilovejuicebar.com/'
    ext = 'locations-1'

    driver = SgSelenium().chrome()
    driver.get(locator_domain + ext)
    states = driver.find_elements_by_css_selector('section.Index-page')[2:]
    link_list = []
    for state in states:
        ps = state.find_elements_by_tag_name("p")
        for p in ps:
            try:
                href = p.find_element_by_tag_name('a').get_attribute('href')
                if "locations-1" not in href:
                    main = p.text.replace("105 Franklin","105\nFranklin").split("\n")
                    link_list.append([href,main])
            except:
                pass

    all_store_data = []
    for row in link_list:
        link = row[0]
        driver.get(link)
        print(link)
        time.sleep(2)
        element = WebDriverWait(driver, 30).until(EC.presence_of_element_located(
            (By.CLASS_NAME, "Main-content")))
        time.sleep(2)
        main = driver.find_element_by_css_selector('section.Main-content').text.split('\n')
        
        if "brand that was founded" in main[0] and link == "https://ilovejuicebar.com/troy":
            location_name = "Troy"
            street_address = "3115 Crooks Road"
            city = "Troy"
            state = "Michigan"
            zip_code = "48084"
            store_data = [locator_domain, link, location_name, street_address, city, state, zip_code, country_code,
                          '<MISSING>', '<MISSING>', '<MISSING>', '<MISSING>', '<MISSING>', '<MISSING>']
            all_store_data.append(store_data)
            continue

        raw_address = row[1]
        if not raw_address[-1].strip():
            raw_address.pop(-1)

        street_address = " ".join(raw_address[:-1])
        city, state, zip_code = addy_ext(raw_address[-1])
        location_name = raw_address[0].strip()

        hours = ''
        phone_number = ''
        for h in main:
            if '//' in h or "am-" in h or "am -" in h:
                hours += h + ' '
            if re.search('([\-\+]{0,1}\d[\d\.\,]*[\.\,][\d\.\,]*\d+)', h):
                phone_number = re.search('([\-\+]{0,1}\d[\d\.\,]*[\.\,][\d\.\,]*\d+)', h).group()
            else:
                try:
                    phone_number = re.findall(r'[0-9]{3}-[0-9]{3}-[0-9]{4}', h)[0]
                except:
                    pass

        hours = hours.replace("–","-").strip()

        if hours == '':
            hours = '<MISSING>'
        if phone_number == '':
            phone_number = '<MISSING>'
        data = driver.find_element_by_css_selector('div.sqs-block.map-block.sqs-block-map').get_attribute(
            'data-block-json')
        json_coord = json.loads(data)

        lat = json_coord['location']['markerLat']
        longit = json_coord['location']['markerLng']

        location_type = '<MISSING>'
        store_number = '<MISSING>'
        country_code = 'US'
        store_data = [locator_domain, link, location_name, street_address.strip(), city, state, zip_code, country_code,
                      store_number, phone_number, location_type, lat, longit, hours]
        all_store_data.append(store_data)

    driver.quit()
    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
