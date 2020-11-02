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

def addy_ext_us(addy):
    addy = addy.split(',')
    city = addy[0]
    state_zip = addy[1].strip().split(' ')
    if len(state_zip) == 3:
        state = state_zip[0] + ' ' + state_zip[1]
        zip_code = state_zip[2]
    else:
        state = state_zip[0]
        zip_code = state_zip[1]
    return city, state, zip_code, 'US'

def addy_ext_can(addy):
    addy = addy.split(',')
    city = addy[0]
    state_zip = addy[1].strip().split(' ')
    if len(state_zip[-1]) == 3:
        if len(state_zip) == 4:
            state = state_zip[0] + ' ' + state_zip[1]
            zip_code = state_zip[2] + ' ' + state_zip[3]
        elif len(state_zip) == 5:
            state = state_zip[0] + ' ' + state_zip[1] + ' ' + state_zip[2]
            zip_code = state_zip[3] + ' ' + state_zip[4]

        else:
            state = state_zip[0]
            zip_code = state_zip[1] + ' ' + state_zip[2]
    else:
        if len(state_zip) == 3:
            state = state_zip[0] + ' ' + state_zip[1]
            zip_code = state_zip[2]
        elif len(state_zip) == 4:
            state = state_zip[0] + ' ' + state_zip[1] + ' ' + state_zip[2]
            zip_code = state_zip[3]

        else:
            state = state_zip[0]
            zip_code = state_zip[1]

    return city, state, zip_code, 'CA'

def fetch_data():
    locator_domain = 'https://www.irvingoil.com/'
    ext = 'en-US/location'

    driver = SgSelenium().chrome()
    driver.get(locator_domain + ext)
    driver.implicitly_wait(30)
    locs = driver.find_elements_by_css_selector('a.link__details')
    link_list = []
    for loc in locs:
        link = loc.get_attribute('href')
        link_list.append(link)

    all_store_data = []
    for link in link_list:
        if link == 'https://www.irvingoil.com/location/irving-oil':
            continue
            
        driver.get(link)
        driver.implicitly_wait(4)
        
        location_name = '<MISSING>'
        try:
            addy = driver.find_element_by_css_selector('div.location__address').text.split('\n')
        except:
            continue
        
        street_address = addy[0]
        if addy[2] == 'Canada':
            city, state, zip_code, country_code = addy_ext_can(addy[1])
        else:
            city, state, zip_code, country_code = addy_ext_us(addy[1])
            
        hours_div = driver.find_elements_by_css_selector('div.location__hours')
        hours = ''
        for h in hours_div:
            if h.text.strip() == '':
                continue
            if '24 hours' in h.text:
                hours = 'Open 24 Hours'
                break
            hours = h.text.replace('\n', ' ').replace('Store Hours', '').strip()

        if hours == '':
            hours = '<MISSING>'

        lat = driver.find_element_by_css_selector('div.location__latitude').text.split('\n')[-1]
        longit = driver.find_element_by_css_selector('div.location__longitude').text.split('\n')[-1]
        
        phone_number = driver.find_element_by_css_selector('div.field--name-field-site-phone-number').text
        if phone_number == '':
            phone_number = '<MISSING>'
        
        store_number = link.split('-')[-1]
        if store_number.isdigit() == False:
            store_number = '<MISSING>'

        page_url = link
        location_type = '<MISSING>'
        store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code, 
                    store_number, phone_number, location_type, lat, longit, hours, page_url]

        all_store_data.append(store_data)
        
    driver.quit()
    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
