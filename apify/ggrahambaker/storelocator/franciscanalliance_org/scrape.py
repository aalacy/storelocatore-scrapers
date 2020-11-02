import csv
import os
from sgselenium import SgSelenium
from selenium.webdriver.support.ui import Select
import time
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('franciscanalliance_org')



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
    state_zip = ' '.join(addy[1].split()).split(' ')
    state = state_zip[0]
    zip_code = state_zip[1].split('-')[0]#.strip()
    return city, state, zip_code

def fetch_data():
    locator_domain = 'https://www.franciscanhealth.org/'
    ext = 'healthcare-facilities'

    driver = SgSelenium().chrome()
    driver.get(locator_domain + ext)

    menu = driver.find_element_by_css_selector('div.location-facility-type')
    menu.click()
    driver.implicitly_wait(5)
    time.sleep(2)
    location_types = []
    for t in menu.find_elements_by_css_selector('li'):
        location_types.append(t.text)

    driver.get(locator_domain + ext)
    driver.implicitly_wait(5)
    all_store_data = []

    dup_tracker = set()

    for i, loc_type in enumerate(location_types):
        logger.info(loc_type)
        time.sleep(2)
        menu = driver.find_element_by_css_selector('div.location-facility-type')
        menu.click()
        driver.implicitly_wait(5)

        to_click = menu.find_elements_by_css_selector('li')[i]
        to_click.click()
        driver.implicitly_wait(5)
        
        while True:
            time.sleep(3)
            locs = driver.find_elements_by_css_selector('div.location')
            for loc in locs:
                loc_name = loc.find_element_by_css_selector('a.facility-name')
                location_name = loc_name.text
                page_url = loc_name.get_attribute('href')
                if location_name not in dup_tracker:
                    dup_tracker.add(location_name)
                else:
                    continue

                infos = loc.find_elements_by_css_selector('p')#.text
                addy = infos[0].text.replace('Contact:', '').strip().split('\n')
           
                if addy[0].split(' ')[0].split('-')[0].isdigit() == False:
                    if 'Bill Long Building' not in addy[0]:
                        addy = addy[1:]

                if '2030 Churchman Avenue' in addy[0] and len(addy) == 5:
                    addy = addy[:-1]
                if '3500 Franciscan Way' in addy[0] and len(addy) == 4:
                    if 'First' not in addy[1]:
                        addy = addy[:-1]

                if len(addy) == 3:
                    street_address = addy[0]
                    city, state, zip_code = addy_ext(addy[1])
                    phone_number = addy[2]
                elif len(addy) == 4:
                    street_address = addy[0]
                    city, state, zip_code = addy_ext(addy[2])
                    phone_number = addy[3]
                
                else:
                    street_address = addy[0]
                    city, state, zip_code = addy_ext(addy[1])
                    phone_number = '<MISSING>'
                    
                street_address = street_address.split(',')[0]
                if len(infos) == 2:
                    hours = infos[1].text.replace('Office Hours:', '').replace('\n', ' ').strip()
                else:
                    hours = '<MISSING>'
                    
                links = loc.find_elements_by_css_selector('a')
                for l in links:
                    if '/maps/' in l.get_attribute('href'):
                        coords = l.get_attribute('href').split('Location/')[1].split(',')
                        lat = coords[0]
                        longit = coords[1]
                
                country_code = 'US'
                store_number = '<MISSING>'
                
                store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code, 
                            store_number, phone_number, loc_type, lat, longit, hours, page_url]

                all_store_data.append(store_data)
            
            if len(driver.find_elements_by_css_selector('i.fa-angle-right')) < 2:
                break
            else:
                driver.find_elements_by_css_selector('i.fa-angle-right')[0].click()
                driver.implicitly_wait(5)

    driver.quit()
    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
