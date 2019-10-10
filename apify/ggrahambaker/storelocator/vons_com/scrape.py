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
    locator_domain = 'https://local.vons.com/'
    ext = 'index.html'

    driver = get_driver()
    driver.get(locator_domain + ext)

    links = driver.find_elements_by_css_selector('a.c-directory-list-content-item-link')

    state_list = []
    for li in links:
        state_list.append(li.get_attribute('href'))

    store_list = []
    more_stores = []
    for state in state_list:
        driver.get(state)
        driver.implicitly_wait(10)

        list_items = driver.find_elements_by_css_selector('li.c-directory-list-content-item')
        for li in list_items:
            num_stores = int(li.find_element_by_css_selector('span').text[1:-1])

            if num_stores > 1:
                more_stores.append(li.find_element_by_css_selector('a').get_attribute('href'))
            else:
                store_list.append(li.find_element_by_css_selector('a').get_attribute('href'))

    for more in more_stores:
        driver.get(more)
        driver.implicitly_wait(10)
        links = driver.find_elements_by_css_selector('a.Teaser-nameLink')
        for li in links:
            store_list.append(li.get_attribute('href'))

    all_store_data = []
    for link in store_list:
        driver.get(link)
        driver.implicitly_wait(10)

        lat = driver.find_element_by_xpath('//meta[@itemprop="latitude"]').get_attribute('content')
        longit = driver.find_element_by_xpath('//meta[@itemprop="longitude"]').get_attribute('content')
        location_name = driver.find_element_by_css_selector('span.LocationName-geo').text

        city = driver.find_element_by_xpath('//meta[@itemprop="addressLocality"]').get_attribute('content')
        street_address = driver.find_element_by_xpath('//meta[@itemprop="streetAddress"]').get_attribute('content')

        state = driver.find_element_by_xpath('//abbr[@itemprop="addressRegion"]').text

        zip_code = driver.find_element_by_xpath('//span[@itemprop="postalCode"]').text

        phone_number = driver.find_element_by_css_selector('span#telephone').text

        data_days = driver.find_element_by_css_selector(
            'div.c-location-hours-details-wrapper.js-location-hours').get_attribute('data-days')
        hours_json = json.loads(data_days)

        hours = ''
        for day in hours_json:
            hours += day['day'] + ' '
            interval = day['intervals'][0]

            start = str(interval['start'])
            end = str(interval['end'])
            if start == '0' and end == '0':
                hours += 'Open 24 Hours '
            else:
                start_time = start[:1] + ':' + start[-2:] + 'am'

                if end == '0':
                    end_time = '12:00 am'
                else:
                    end_time = end[:1] + ':' + end[-2:] + 'am'

                hours += start_time + ' - ' + end_time + ' '

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
