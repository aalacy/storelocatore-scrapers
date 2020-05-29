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

def addy_ext(addy):
    addy = addy.split(',')
    city = addy[0]
    state_zip = addy[1].strip().split(' ')
    state = state_zip[0]
    zip_code = state_zip[1]
    return city, state, zip_code

def fetch_data():
    locator_domain = 'https://giantfitnessclubs.com/'
    ext = 'locations/'

    driver = SgSelenium().chrome()
    driver.get(locator_domain + ext)

    conts = driver.find_elements_by_css_selector('div.column_attr')
    link_list = []
    for c in conts:
        if len(c.find_elements_by_css_selector('a')) == 1:
            link = c.find_element_by_css_selector('a').get_attribute('href')
            
            link_list.append(link)

    all_store_data = []
    for link in link_list:
        driver.get(link)
        driver.implicitly_wait(4)
            
        location_name = driver.find_element_by_css_selector('div#Subheader').text
        
        main = driver.find_element_by_css_selector('div#Content').find_elements_by_css_selector('div.mcb-column')
        
        for div in main:
            if 'Address:' in div.text:
                addy = div.text.split('\n')
                street_address = addy[1]
                city, state, zip_code = addy_ext(addy[2])
                if 'Phone:' in div.text:
                    phone_number = addy[4].replace('Phone:', '').strip()
                    soup = BeautifulSoup(div.get_attribute('innerHTML'), 'html.parser')

                    hours_li = soup.find_all('li')
                    hours = ''
                    for h in hours_li:
                        hours += h.text + ' '
                    
                    hours = ' '.join(hours.split())
    
            elif 'Phone:' in div.text:
                phone_number = div.text.replace('Phone:', '').strip() 
                
            elif 'Hours:' in div.text:
                if 'Pool Hours:' in div.text or 'Childcare' in div.text:
                    continue
                hours = div.text.replace('Hours:', '').strip().replace('\n', ' ')
                hours = ' '.join(hours.split())
                
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
