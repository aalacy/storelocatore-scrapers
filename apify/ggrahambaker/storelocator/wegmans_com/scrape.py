import csv
import os
from sgselenium import SgSelenium
import time

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def addy_ext(addy):
    addy = addy.split(',')
    city = addy[0]
    state_zip = addy[1].strip().split(' ')
    if len(state_zip) == 3:
        state = state_zip[0] + ' ' + state_zip[1]
        zip_code = state_zip[2]

    else:
        state = state_zip[0]
        zip_code = state_zip[1]
    return city, state, zip_code

def fetch_data():
    locator_domain = 'https://www.wegmans.com/'
    ext = 'stores/'

    driver = SgSelenium().chrome()
    driver.get(locator_domain + ext)

    hrefs = driver.find_elements_by_xpath('//a[contains(@href,"/stores/")]')
    link_list = []
    for h in hrefs:
        link = h.get_attribute('href')
        if len(link.split('-')) > 1:
            link_list.append(link)

    all_store_data = []
    for link in link_list:
        driver.get(link)
        driver.implicitly_wait(10)
        time.sleep(3)
        
        main = driver.find_element_by_css_selector('div#wegmans-maincontent')
        location_name = main.find_element_by_css_selector('h1').text
        store_number = main.find_element_by_css_selector('span#store-number').get_attribute('innerHTML')

        addy = driver.find_element_by_css_selector('span#addressHere').text.split('\n')
        street_address = addy[0]
        city, state, zip_code = addy_ext(addy[1])
                
        phone_number = driver.find_element_by_css_selector('span#phoneNumHere').text
        
        hours = main.find_element_by_xpath('..').find_elements_by_css_selector('div.row')[2].text
        
        source = str(driver.page_source)
        for line in source.split('\n'):
            if "new google.maps.LatLng" in line.strip():
                start = line.find('new google.maps.LatLng(') + len('new google.maps.LatLng(')
                coords = line[start:].split(',')
                lat = coords[0]
                longit = coords[1][:-1]
                
        country_code = 'US'
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
