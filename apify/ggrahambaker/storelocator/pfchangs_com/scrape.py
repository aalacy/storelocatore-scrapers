import csv
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
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
    locator_domain = 'https://www.pfchangs.com/'
    ext = 'locations/'

    driver = get_driver()
    driver.get(locator_domain + ext)
    driver.implicitly_wait(10)

    hrefs = driver.find_elements_by_css_selector('a.c-directory-list-content-item-link')

    state_link_list = []
    loc_link_list = []
    for href in hrefs:
        link = href.get_attribute('href')
        if len(link) > 45:
            loc_link_list.append(link)
        else:
            state_link_list.append(link)



    city_link_list = []
    for state in state_link_list:
        driver.get(state)
        driver.implicitly_wait(10)

        hrefs = driver.find_elements_by_css_selector('a.c-directory-list-content-item-link')

        for href in hrefs:
            link = href.get_attribute('href')

            if len(link.split('-')) > 3:
                loc_link_list.append(link)
            else:
                city_link_list.append(link)


    for city in city_link_list:
        driver.get(city)
        driver.implicitly_wait(10)

        locs = driver.find_elements_by_css_selector('div.LocationCard-title')
        for loc in locs:
            link = loc.find_element_by_css_selector('a').get_attribute('href')
            loc_link_list.append(link)


        
    
    all_store_data = []
    for link in loc_link_list:
        driver.get(link)
        driver.implicitly_wait(10)

        location_name = driver.find_element_by_css_selector('div.Hero-title').text
        street_address = driver.find_element_by_css_selector('span.c-address-street').text
        city = driver.find_element_by_css_selector('span.c-address-city').text.replace(',', '').strip()
        state = driver.find_element_by_css_selector('abbr.c-address-state').text
        zip_code = driver.find_element_by_css_selector('span.c-address-postal-code').text

        phone_number = driver.find_element_by_css_selector('span.c-phone-number-span.c-phone-main-number-span').text

        map_html = driver.find_element_by_css_selector('script.js-map-config').get_attribute('innerHTML')
        map_json = json.loads(map_html)
        
        longit = map_json['locs'][0]['longitude']
        lat = map_json['locs'][0]['latitude']
        country_code = 'US'
        page_url = link
        location_type = '<MISSING>'
        store_number = '<MISSING>'
        hours = driver.find_element_by_css_selector('table.c-location-hours-details').text.replace('\n', ' ').replace('Day of the Week', '').strip()

        store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code,
                      store_number, phone_number, location_type, lat, longit, hours, page_url]
        all_store_data.append(store_data)
        

    driver.quit()
    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
