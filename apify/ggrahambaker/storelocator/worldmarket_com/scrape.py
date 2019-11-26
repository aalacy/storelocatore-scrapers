import csv
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
import json

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
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    url = 'https://stores.worldmarket.com/index.html'
    locator_domain = 'https://www.worldmarket.com'
    driver = get_driver()
    driver.get(url)


    locs = driver.find_elements_by_css_selector('a.c-directory-list-content-item-link')
    link_list = []
    state_list = []
    city_list = []
    for loc in locs:
        link = loc.get_attribute('href')
        if len(link) > 38:
            link_list.append(link)
        else:
            state_list.append(link)


    for link in state_list:
        driver.get(link)
        driver.implicitly_wait(10)
        cities = driver.find_elements_by_css_selector('a.c-directory-list-content-item-link')
        for city in cities:        
            city_link = city.get_attribute('href')

            if len(city_link.split('-')) > 2:
                link_list.append(city_link)
            else:
                city_list.append(city_link)

        
    for link in city_list:
        driver.get(link)
        driver.implicitly_wait(10)
        in_cities = driver.find_elements_by_css_selector('a.c-location-grid-item-name-link')
        for loc in in_cities:
            link = loc.get_attribute('href')
            link_list.append(link)


    all_store_data = []
    for link in link_list:
        print(link)
        driver.get(link)
        driver.implicitly_wait(10)
        try:
            lat = driver.find_element_by_xpath('//meta[@itemprop="latitude"]').get_attribute('content')
        except NoSuchElementException:
            continue
        longit = driver.find_element_by_xpath('//meta[@itemprop="longitude"]').get_attribute('content')
        street_address = driver.find_element_by_xpath('//span[@itemprop="streetAddress"]').text
        city = driver.find_element_by_xpath('//span[@itemprop="addressLocality"]').text.replace(',', '').strip()
        state = driver.find_element_by_xpath('//abbr[@itemprop="addressRegion"]').text
        zip_code = driver.find_element_by_xpath('//span[@itemprop="postalCode"]').text
        country_code = 'US'
        store_number = '<MISSING>'
        location_type = '<MISSING>'
        page_url = link
        
        phone_number = driver.find_element_by_xpath('//span[@itemprop="telephone"]').text

        location_name = driver.find_element_by_css_selector('h1#location-name').text.replace('\n', ' ')
        days = driver.find_elements_by_css_selector('tr.c-location-hours-details-row.js-day-of-week-row')
        hours = ''
        for day in days:
            day_hours = day.get_attribute('content')
            if day_hours == None:
                continue
            hours += day_hours + ' '
        
        
        
        store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code,
                        store_number, phone_number, location_type, lat, longit, hours, page_url]
        all_store_data.append(store_data)



    driver.quit()
    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
