import csv
import os
from sgselenium import SgSelenium

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def parse_addy(addy):
    arr = addy.split(',')
    if len(arr) == 4:
        arr = [arr[0], arr[2], arr[3]]
    street_address = arr[0].strip()
    city = arr[1].strip()
    state_zip = arr[2].strip().split(' ')
    state = state_zip[0]
    zip_code = state_zip[1]
    
    return street_address, city, state, zip_code

def fetch_data():
    locator_domain = 'https://primary-health.net/' 
    ext = 'Locations.aspx'
    driver = SgSelenium().chrome()
    driver.get(locator_domain + ext)
    hrefs = driver.find_elements_by_xpath('//a[contains(@href,"LocationDetail.aspx?id=")]')
    links = [h.get_attribute('href') for h in hrefs]

    all_store_data = []
    for link in links:
        driver.get(link)
        driver.implicitly_wait(5)
        
        main = driver.find_element_by_css_selector('div.page-title')
        
        location_name = main.find_element_by_css_selector('h1').text
       
        hours = driver.find_element_by_xpath('//*[@itemprop="openingHours"]').text.replace('\n', ' ').split('PATIENTS')[0].strip()
        if hours == '':
            hours = '<MISSING>'
        
        phone_number = driver.find_element_by_css_selector('span#PageTitle_SiteList2_PhoneLabel_0').text
            
        addy = driver.find_element_by_css_selector('span#PageTitle_SiteList2_AddressLabel_0').text
        street_address, city, state, zip_code = parse_addy(addy)

        country_code = 'US'
        store_number = '<MISSING>'
        location_type = '<MISSING>'
        lat = '<MISSING>'
        longit = '<MISSING>'
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
