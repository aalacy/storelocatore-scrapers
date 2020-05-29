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
    if len(state_zip) == 1:
        state = '<MISSING>'
        zip_code = state_zip[0]
    else:
        state = state_zip[0]
        zip_code = state_zip[1]
    return city, state, zip_code

def fetch_data():
    locator_domain = 'https://www.amitahealth.org/'
    ext = 'our-locations/'

    driver = SgSelenium().chrome()
    driver.get(locator_domain + ext)

    past_urls = []
    link_list = []
    for i in range(1, 15):
        url = 'https://www.amitahealth.org/our-locations/?page=' + str(i) + '&count=50'
        driver.get(url)
        driver.implicitly_wait(5)
        time.sleep(3)
        curr_url = driver.current_url
        if curr_url not in past_urls:
            past_urls.append(curr_url)
        else:
            break
            
        locs = driver.find_elements_by_css_selector('div.stacked-md')
        for loc in locs:
            link = loc.find_element_by_css_selector('a').get_attribute('href')
            if link not in link_list:
                link_list.append(link)
            else:
                continue

    all_store_data = []
    for link in link_list:
        if link == 'https://www.amitahealth.org/location/amita-health-medical-group':
            continue
        driver.get(link)
        driver.implicitly_wait(5)
        
        location_name = driver.find_element_by_css_selector('h1').text
        google_link = driver.find_element_by_xpath('//a[contains(@href,"/maps/")]').get_attribute('href')
        
        start = google_link.find('query=')
        coords = google_link[start + 6:].split('%2C')
        lat = coords[0]
        longit = coords[1]
        
        addy = driver.find_element_by_xpath('//strong[contains(text(),"Address")]').find_element_by_xpath('..').text.split('\n')
        
        street_address = addy[1].split('Ste.')[0].strip()
        if '1600 W. Rte. 6' in street_address:
            street_address = '1600 W. Rte. 6'
        elif '830 W. Diversey Pkwy' in street_address:
            street_address = '830 W. Diversey Pkwy'
        elif 'S. Rt. 59' in street_address:
            street_address = street_address
        elif '420 S. Schmidt Ave' in street_address:
            street_address = '420 S. Schmidt Ave'
        else:
            end = street_address.rfind('.')
            if end > 0:
                street_address = street_address[:end]
            else:
                street_address = street_address

        city, state, zip_code = addy_ext(addy[2])

        phone_number = driver.find_element_by_xpath('//strong[contains(text(),"Phone")]').find_element_by_xpath('..').text
        phone_number = phone_number.replace('Phone:', '').strip()
        if phone_number == '':
            phone_number = '<MISSINg>'
        
        hours_div = driver.find_elements_by_xpath('//label[contains(text(),"Office Hours")]')#.text
        if len(hours_div) == 0:
            hours = '<MISSING>'
        else:
            hours = hours_div[0].find_element_by_xpath('..').text.replace('Office Hours', '').replace('\n', ' ').strip()
        
        country_code = 'US'
        store_number = '<MISSING>'
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
