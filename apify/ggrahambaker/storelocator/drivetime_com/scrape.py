import csv
import os
from sgselenium import SgSelenium
import time
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
    locator_domain = 'https://www.drivetime.com/'
    ext = 'used-car-dealers'

    driver = SgSelenium().chrome()
    driver.get(locator_domain + ext)
    driver.implicitly_wait(10)
    time.sleep(2)

    ul = driver.find_element_by_css_selector('ol.link-swamp-list')
    lis = ul.find_elements_by_css_selector('a.inline-link')
    
    state_list = []
    for li in lis:
        state_list.append(li.get_attribute('href'))

    link_list = []
    for state in state_list:
        driver.get(state)
        driver.implicitly_wait(10)
        swamp = driver.find_element_by_css_selector('ol.link-swamp-list')
        lis = swamp.find_elements_by_css_selector('a')
        for li in lis:
            link_list.append(li.get_attribute('href'))

    all_store_data = []
    for link in link_list:
        driver.get(link)
        driver.implicitly_wait(10)
        time.sleep(4)
        try:
            content = driver.find_element_by_css_selector('div.dealership-details-container').get_attribute('innerHTML')
        except:
            print('sleeeeep')
            time.sleep(10)
            content = driver.find_element_by_css_selector('div.dealership-details-container').get_attribute('innerHTML')
        
        #print(content)
        soup = BeautifulSoup(content, 'html.parser')

        location_name = soup.find('h1', {'class': 'dealer-top-header'}).text
        location_name += ' ' + soup.find('h2', {'class': 'dealer-sub-header'}).text

        street_address = soup.find('span', {'itemprop': 'streetAddress'}).text
        city = soup.find('span', {'itemprop': 'addressLocality'}).text
        state = soup.find('span', {'itemprop': 'addressRegion'}).text
        zip_code = soup.find('span', {'itemprop': 'postalCode'}).text

        phone_and_map = soup.find('div', {'class': 'address-contact'}).find_all('a')
        phone_number = phone_and_map[0]['href'].replace('tel:','')
        map_link = phone_and_map[1]['href']
        start = map_link.find('latLng=') + 7
        coords = map_link[start:].split(',')
        lat = coords[0]
        longit = coords[1].split('&')[0]

        hours = ''
        hours_metas = soup.find_all('meta', {'itemprop': 'openingHours'})
        for meta in hours_metas:
            hours += meta['content'] + ' '
            
        country_code = 'US'
        store_number = '<MISSING>'
        location_type = '<MISSING>'
        store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code,
                      store_number, phone_number, location_type, lat, longit, hours, link]
        all_store_data.append(store_data)

    driver.quit()
    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
