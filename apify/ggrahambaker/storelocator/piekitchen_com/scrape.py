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

def addy_ext(addy):
    address = addy.split(',')
    city = address[0]
    state_zip = address[1].strip().split(' ')
    state = state_zip[0]
    zip_code = state_zip[1]
    return city, state, zip_code

def fetch_data():
    locator_domain = 'https://www.piekitchen.com/'
    ext = 'locations.html'

    driver = SgSelenium().chrome()
    driver.get(locator_domain + ext)

    maps = driver.find_elements_by_css_selector('iframe')

    all_store_data = []
    for gmap in maps: 

        href = gmap.get_attribute('src')
        start_idx = href.find('&long=') + 6
        end_idx = href.find('&domain')

        coords = href[start_idx:end_idx].split('&lat=')
        longit = coords[0]
        lat = coords[1]

        parent = gmap.find_element_by_xpath('../../..') 
        paras = parent.find_elements_by_css_selector('div.paragraph')
      
        if len(paras) == 4:
            addy_phone = paras[0].text.split('\n')
            h = paras[1].text.replace('Hours', '').strip().replace('\n', ' ')
        elif len(paras) == 2:
            addy_phone = paras[0].text.split('\n')
            h = paras[1].text.replace('Hours', '').strip().replace('\n', ' ')
        else:
            continue

        location_name = addy_phone[0]
        street_address = addy_phone[1]
        city, state, zip_code = addy_ext(addy_phone[2])
        phone_number = addy_phone[3]
        
        hours = ' '.join(h.split())

        country_code = 'US'
        store_number = '<MISSING>'
        location_name = '<MISSING>'
        location_type = '<MISSING>'
        page_url = '<MISSING>'

        store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code,
                      store_number, phone_number, location_type, lat, longit, hours, page_url]
        all_store_data.append(store_data)

    driver.quit()
    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
