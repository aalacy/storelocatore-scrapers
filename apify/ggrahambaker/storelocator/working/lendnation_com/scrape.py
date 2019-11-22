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
    locator_domain = 'https://www.lendnation.com/'
    ext = 'location/index.html'

    driver = get_driver()
    driver.get(locator_domain + ext)


    states = driver.find_elements_by_css_selector('li.Directory-listItem')
    state_links = []
    for state in states:
        link = state.find_element_by_css_selector('a').get_attribute('href')
        state_links.append(link)

    
    url_list = []
    for link in state_links:
        driver.get(link)
        driver.implicitly_wait(10)
        
        locs = driver.find_element_by_css_selector('script#js-map-config-dir-map-2')
        loc_json = json.loads(locs.get_attribute('innerHTML'))
        for location in loc_json['locs']:
            lat = location['latitude']
            longit = location['longitude']
            url = location['url']
            
            url_list.append([url, lat, longit])
            


    link_list = []
    for url_ext in url_list:
        url = 'https://www.lendnation.com/location/' + url_ext[0]
        driver.get(url)
        driver.implicitly_wait(10)

        store_links = driver.find_elements_by_css_selector('a.Teaser-titleLink')
        for link in store_links:
            link_list.append(link.get_attribute('href'))

    all_store_data = []
    for link in link_list:
        driver.get(link)
        driver.implicitly_wait(10)

        location_name = driver.find_element_by_css_selector('div.Nap-title.Heading--lead').text
        
        lat = driver.find_element_by_xpath('//meta[@itemprop="latitude"]').get_attribute('content')
        longit = driver.find_element_by_xpath('//meta[@itemprop="longitude"]').get_attribute('content')

        city = driver.find_element_by_xpath('//meta[@itemprop="addressLocality"]').get_attribute('content')
        street_address = driver.find_element_by_xpath('//meta[@itemprop="streetAddress"]').get_attribute('content')

        state = driver.find_element_by_xpath('//abbr[@itemprop="addressRegion"]').text
        zip_code = driver.find_element_by_xpath('//span[@itemprop="postalCode"]').text

        phone_number = driver.find_element_by_css_selector('span#telephone').text

        days_json = json.loads(driver.find_element_by_css_selector('div.c-location-hours-details-wrapper.js-location-hours').get_attribute('data-days'))
        hours = ''
        for week_day in days_json:
            day_name = week_day['day']
            if len(week_day['intervals']) == 0:
                day_string = day_name + ': Closed'
            else:
                start = week_day['intervals'][0]['start']
                end = week_day['intervals'][0]['end']

                day_string = day_name + ' : ' + str(start) + ' - ' + str(end)

            hours += day_string + ' '

        hours = hours.strip()


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
