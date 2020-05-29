import csv
import os
from sgselenium import SgSelenium
import json



def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    locator_domain = 'https://www.batteriesplus.com/'
    ext = 'store-locator'

    driver = SgSelenium().chrome()
    driver.get(locator_domain + ext)

    main = driver.find_element_by_css_selector('div.locator-states')
    states = main.find_elements_by_css_selector('a')
    state_list = []
    for state in states:
        state_list.append(state.get_attribute('href'))

    city_list = []
    for state in state_list:
        driver.get(state)
        driver.implicitly_wait(10)
        
        cities = driver.find_elements_by_xpath("//a[contains(text(),'More Info')]")
        
        for c in cities:
        
            city_list.append(c.get_attribute('href'))


    all_store_data = []
    dup_tracker = []
    for i, link in enumerate(city_list):
        driver.get(link)
        driver.implicitly_wait(10)
        loc_info = driver.execute_script('return storeListJson')[0]


        if loc_info['Address2'] == None:
            street_address = loc_info['Address1']
        else:
            street_address = loc_info['Address1'] + ' ' + loc_info['Address2']

        
        city = loc_info['City']
        state = loc_info['State']
        zip_code = loc_info['ZipCode']
        
        store_number = loc_info['StoreId']
        
        hours = loc_info['MonThuHours'] + ' ' + loc_info['FriHours'] + ' ' + loc_info['SatHours'] + ' ' + loc_info['SunHours'] 
        
        lat = loc_info['Latitude']
        longit = loc_info['Longitude']
        phone_number = loc_info['Phone']
        if link not in dup_tracker:
            dup_tracker.append(link)
        else:
            continue
        
        if loc_info['IsOpeningSoon']:

            continue

        country_code = 'US'

        location_name = city + ', ' + state
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
