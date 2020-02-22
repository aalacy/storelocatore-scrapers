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

    hrefs = driver.find_elements_by_css_selector('a.Directory-listLink')

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

        hrefs = driver.find_elements_by_css_selector('a.Directory-listLink')

        for href in hrefs:
            link = href.get_attribute('href')
            if len(link.split('-')) > 3:
                loc_link_list.append(link)
            else:
                city_link_list.append(link)


    for city in city_link_list:
        driver.get(city)
        driver.implicitly_wait(10)

        locs = driver.find_elements_by_css_selector('a.Teaser-titleLink')
        for loc in locs:
            link = loc.get_attribute('href')
            loc_link_list.append(link)


        
    
    all_store_data = []
    for link in loc_link_list:
        driver.get(link)
        driver.implicitly_wait(10)

        location_name = driver.find_element_by_css_selector('span#location-name').text
        
        street_address = driver.find_element_by_css_selector('span.c-address-street-1').text
        if len(driver.find_elements_by_css_selector('span.c-address-street-2')) == 1:
            street_address += ' ' + driver.find_element_by_css_selector('span.c-address-street-2').text

        city = driver.find_element_by_css_selector('span.c-address-city').text.replace(',', '').strip()
        state = driver.find_element_by_css_selector('abbr.c-address-state').text
        zip_code = driver.find_element_by_css_selector('span.c-address-postal-code').text

        phone_number = driver.find_element_by_css_selector('div#phone-main').text


        coords = driver.find_element_by_xpath('//meta[@name="geo.position"]').get_attribute('content').split(';')
        lat = coords[0]
        longit = coords[1]
 
        country_code = 'US'
        page_url = link
        location_type = '<MISSING>'
        store_number = '<MISSING>'
        hours_td = driver.find_element_by_css_selector('div.js-hours-table').get_attribute('data-days')
        hours_json = json.loads(hours_td)
        hours = ''
        for h in hours_json:
            day = h['day']
            if len(h['intervals']) == 0:
                hours += day + ' Closed '
            else:
                start = h['intervals'][0]['start']
                end = h['intervals'][0]['end']

                hours += day + ' ' + str(start) + ' - ' + str(end) + ' '
            
        store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code,
                      store_number, phone_number, location_type, lat, longit, hours, page_url]
        

        all_store_data.append(store_data)
        

    driver.quit()
    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
