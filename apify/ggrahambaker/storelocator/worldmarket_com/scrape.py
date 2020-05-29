import csv
import os
from sgselenium import SgSelenium
from selenium.common.exceptions import NoSuchElementException
import json
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
    url = 'https://stores.worldmarket.com/index.html'
    locator_domain = 'https://www.worldmarket.com'
    driver = SgSelenium().chrome()
    driver.get(url)

    locs = driver.find_elements_by_css_selector('a.c-directory-list-content-item-link')
    link_list = []
    state_list = []
    city_list = []
    for loc in locs:
        link = loc.get_attribute('href')
        
        if len(link) > 38:
            
            if 'brooklyn.html' in link:
                city_list.append(link)
            else:
                link_list.append(link)
        else:
            state_list.append(link)

    for link in state_list:
        driver.get(link)
        driver.implicitly_wait(10)
        cities = driver.find_elements_by_css_selector('a.c-directory-list-content-item-link')
        for city in cities:      
            
            city_link = city.get_attribute('href')

            if len(city_link.split('/')) > 5:
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
        driver.get(link)
        driver.implicitly_wait(10)
        is_bed = False
        try:
            lat = driver.find_element_by_xpath('//meta[@itemprop="latitude"]').get_attribute('content')
        except NoSuchElementException:
            time.sleep(5)
            if 'bedbathandbeyond' in driver.current_url:
       
                is_bed = True
            else:
                continue

        if is_bed:
            hours = driver.find_element_by_id('store-hours').text.replace('Store Hours', '').replace('/n', ' ')
            
            hours = ' '.join(hours.split())
            lat = '<MISSING>'
            longit = '<MISSING>'

            phone_number = driver.find_element_by_xpath("//span[contains(text(), 'World Market')]").text.replace('World Market', '').strip()
            
            location_name = 'Liberty View'
            state = driver.find_element_by_xpath('//span[@itemprop="addressRegion"]').text
            zip_code = '<MISSING>'
        
        else:
            longit = driver.find_element_by_xpath('//meta[@itemprop="longitude"]').get_attribute('content')
            location_name = driver.find_element_by_css_selector('h1#location-name').text.replace('\n', ' ')
            phone_number = driver.find_element_by_xpath('//span[@itemprop="telephone"]').text
            state = driver.find_element_by_xpath('//abbr[@itemprop="addressRegion"]').text
            zip_code = driver.find_element_by_xpath('//span[@itemprop="postalCode"]').text
            days = driver.find_elements_by_css_selector('tr.c-location-hours-details-row.js-day-of-week-row')
            hours = ''
            for day in days:
                day_hours = day.get_attribute('content')
                if day_hours == None:
                    continue
                hours += day_hours + ' '

        street_address = driver.find_element_by_xpath('//span[@itemprop="streetAddress"]').text
        city = driver.find_element_by_xpath('//span[@itemprop="addressLocality"]').text.replace(',', '').strip()
        
        country_code = 'US'
        store_number = '<MISSING>'
        location_type = '<MISSING>'
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
