import csv
import os
from sgselenium import SgSelenium
from bs4 import BeautifulSoup

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    locator_domain = 'https://www.rockandbrews.com/'
    ext = 'locations/'

    driver = SgSelenium().chrome()
    driver.get(locator_domain + ext)
    locs = driver.find_elements_by_css_selector('li.location')

    data_list = []

    for loc in locs:
        location_name = loc.get_attribute('data-name')
        lat = loc.get_attribute('data-latitude')
        longit = loc.get_attribute('data-longitude')
        
        if loc.get_attribute('data-country') != 'usa':
            continue
            
        url = locator_domain[:-1] + loc.get_attribute('data-href')
        
        data_list.append([url, location_name, lat, longit])

    dup_tracker = set()
    all_store_data = []
    for data in data_list:
        page_url = data[0]
        if page_url not in dup_tracker:
            dup_tracker.add(page_url)
        else:
            continue
        location_name = data[1]
        lat = data[2]
        longit = data[3]
        
        driver.get(page_url)
        driver.implicitly_wait(5)
        
        try:
            phone_number = driver.find_element_by_css_selector('a.phone-link').text
        except:
            phone_number = '<MISSING>'

        if 'att-center/' in page_url:
            phone_number = '(818) 574-3220'
        
        street_address = driver.find_element_by_xpath('//span[@itemprop="streetAddress"]').text.replace('\n', ' ')
        city = driver.find_element_by_xpath('//span[@itemprop="addressLocality"]').text
        
        state = driver.find_element_by_xpath('//span[@itemprop="addressRegion"]').text
        
        zip_code = driver.find_element_by_xpath('//span[@itemprop="postalCode"]').text

        try:
            hours_div = driver.find_element_by_css_selector('div#LocalMapAreaOpenHourBanner').get_attribute('innerHTML')
            
            soup = BeautifulSoup(hours_div, 'html.parser').find_all('li')
            hours = ''
            for li in soup:
                hours += li.text.replace('\n', ' ').replace('See More Hours', '').strip() + ' '
                
            if hours == '':
                hours = '<MISSING>'
        except:
            hours = '<MISSING>'
        
        country_code = 'US'
        store_number = '<MISSING>'
        location_type = '<MISSING>'
        
        store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code, 
                    store_number, phone_number, location_type, lat, longit, hours, page_url]

        all_store_data.append(store_data)
        
    driver.quit()
    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
