from sgrequests import SgRequests
from bs4 import BeautifulSoup
import csv
import os
from sgselenium import SgSelenium
import json
import time
from random import randint
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    locator_domain = 'https://www.lendnation.com/'
    ext = 'location/index.html'

    driver = SgSelenium().chrome()
    driver.get(locator_domain + ext)

    states = driver.find_elements_by_css_selector('li.Directory-listItem')
    state_links = []
    for state in states:
        link = state.find_element_by_css_selector('a').get_attribute('href')
        state_links.append(link)

    url_list = []
    for link in state_links:
        print(link)
        driver.get(link)

        time.sleep(randint(2,4))
        element = WebDriverWait(driver, 20).until(EC.presence_of_element_located(
            (By.CLASS_NAME, "js-map-config")))
        time.sleep(randint(1,2))
        
        locs = driver.find_element_by_css_selector('.js-map-config')
        loc_json = json.loads(locs.get_attribute('innerHTML'))
        for location in loc_json['locs']:
            lat = location['latitude']
            longit = location['longitude']
            url = location['url']
            
            url_list.append([url, lat, longit])

    link_list = []
    for url_ext in url_list:
        url = 'https://www.lendnation.com/location/' + url_ext[0]
        link_list.append(url)
        
    user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'
    HEADERS = {'User-Agent' : user_agent}

    session = SgRequests()

    all_store_data = []
    for link in link_list:
        print(link)
        req = session.get(link, headers = HEADERS)
        time.sleep(randint(1,2))
        try:
            base = BeautifulSoup(req.text,"lxml")
        except (BaseException):
            print('[!] Error Occured. ')
            print('[?] Check whether system is Online.')

        location_name = base.h1.text.strip()
        
        lat = base.find('meta', attrs={'itemprop': "latitude"})['content']
        longit = base.find('meta', attrs={'itemprop': "longitude"})['content']

        city = base.find('meta', attrs={'itemprop': "addressLocality"})['content']
        street_address = base.find('meta', attrs={'itemprop': "streetAddress"})['content']
        state = base.find('abbr', attrs={'itemprop': "addressRegion"}).text
        zip_code = base.find('span', attrs={'itemprop': "postalCode"}).text
        phone_number = base.find('span', attrs={'itemprop': "telephone"}).text

        hours = base.find(class_="c-location-hours-details").text.replace("Day of the WeekHours","").replace("PM", "PM ").strip()

        store_number = '<MISSING>'
        location_type = '<MISSING>'
        country_code = 'US'
        page_url = link

        store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code,
                      store_number, phone_number, location_type, lat, longit, hours, page_url]

        all_store_data.append(store_data)

    driver.quit()
    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
