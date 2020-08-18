import csv
import os
from sgselenium import SgSelenium
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import time

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    locator_domain = 'https://www.academy.com/'
    ext = 'shop/storelocator'

    driver = SgSelenium().chrome()
    driver.get(locator_domain + ext)

    driver.implicitly_wait(10)

    state_links = [a_tag.get_attribute('href') for a_tag in driver.find_elements_by_css_selector('a.stateLinks')]
    link_list = []
    for state in state_links:
        print(state)
        driver.get(state)
        driver.implicitly_wait(10)
        city_links = [a_tag.get_attribute('href') for a_tag in driver.find_elements_by_css_selector('a.cityLinks')]
        for city in city_links:
            print(city)
            driver.get(city)
            driver.implicitly_wait(10)
            n_links = driver.find_elements_by_css_selector('a.neighborhoodLinks')
            for n_link in n_links:
                link = n_link.get_attribute('href')
                link_list.append(link)

    session = SgRequests()
    HEADERS = { 'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36' }

    all_store_data = []

    for i, link in enumerate(link_list):
        print("Link %s of %s" %(i+1,len(link_list)))
        print(link)
        r = session.get(link, headers = HEADERS)
        soup = BeautifulSoup(r.content, 'html.parser')
        try:
            loc = soup.find('input', {'id': 'params'})
            street_address = loc['data-address']
        except:
            time.sleep(10)
            r = session.get(link, headers = HEADERS)
            soup = BeautifulSoup(r.content, 'html.parser')
            loc = soup.find('input', {'id': 'params'})

        try:
            street_address = loc['data-address']
        except:
            driver.get(link)
            driver.implicitly_wait(30)
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            loc = soup.find('input', {'id': 'params'})

        street_address = loc['data-address']
        city = loc['data-city']
        state = loc['data-state'].title()
        zip_code = loc['data-zip']
        if len(zip_code) < 5:
            zip_code = '<MISSING>'
        lat = loc['data-lat']
        longit = loc['data-lng']
        location_name = loc['data-neighborhood'].strip()
        phone_number = loc['data-phone']
        
        hours = ''
        days = soup.find('div', {'id': 'storeHoursContainer'}).find_all('time', {'itemprop': 'openingHours'})
        
        for day in days:
            hours += day['datetime'] + ' '
        hours = hours.strip()

        country_code = 'US'
        location_type = '<MISSING>'
        page_url = link
        store_number = link.split('store-')[1]
        store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code,
                    store_number, phone_number, location_type, lat, longit, hours, page_url]

        all_store_data.append(store_data)

    driver.quit()
    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
