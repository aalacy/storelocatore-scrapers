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

def fetch_data():
    locator_domain = 'https://oncueexpress.com/'
    ext = 'find-a-store'
    driver = SgSelenium().chrome()

    all_store_data = []
   
    dup_tracker = set()
    last = driver.find_elements_by_css_selector('li.pager-last')
    done = True

    for i in range(15):
        driver.get('https://oncueexpress.com/find-a-store?page=' + str(i))
        driver.implicitly_wait(10)
        time.sleep(5)
        locs = driver.find_elements_by_css_selector('div.node-content')
        if len(locs) == 1:
            break
        for loc in locs:
            location_name = loc.find_element_by_css_selector('div.title').text        
            store_number = location_name.split('#')[1].strip()
            
            street_address= loc.find_element_by_css_selector('div.thoroughfare').text
            
            city = loc.find_element_by_css_selector('span.locality').text
            state = loc.find_element_by_css_selector('span.state').text
            zip_code = loc.find_element_by_css_selector('span.postal-code').text
            
            country_code = 'US'
            location_type = '<MISSING>'
            lat = '<MISSING>'
            longit = '<MISSING>'
            hours = '<MISSING>'
            page_url = '<MISSING>'
            phone_number_div = loc.find_elements_by_css_selector('div.phone-number')
            
            if len(phone_number_div) == 1:
                phone_number = phone_number_div[0].text.replace('Phone:', '').strip()
            else:
                phone_number = '<MISSING>'

            if store_number not in dup_tracker:
                if phone_number == '<MISSING>':
                    continue
                dup_tracker.add(store_number)
            else:
                continue
            
            store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code, 
                        store_number, phone_number, location_type, lat, longit, hours, page_url]

            all_store_data.append(store_data)
            
    driver.quit()
    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
