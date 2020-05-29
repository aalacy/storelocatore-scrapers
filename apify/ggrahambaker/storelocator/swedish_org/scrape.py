import csv
import os
from sgselenium import SgSelenium
from selenium.webdriver.support.ui import Select
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
    state = state_zip[0]
    zip_code = state_zip[1]
    return city, state, zip_code

def fetch_data():
    locator_domain = 'https://www.swedish.org/'
    ext = 'locations/list-view?loctype=birth+center&within=5000'

    driver = SgSelenium().chrome()

    driver.get(locator_domain + ext)
    driver.implicitly_wait(5)
    time.sleep(5)

    opts = driver.find_element_by_id('main_0_leftpanel_0_ddlLocationType').find_elements_by_css_selector('option')
    types = []
    for opt in opts:
        o = opt.get_attribute('value').strip()
        if o == '':
            continue
        types.append(o)

    link_list = []

    for t in types:
        butt = driver.find_element_by_id('main_0_leftpanel_0_btnSubmit')
        select = Select(driver.find_element_by_id('main_0_leftpanel_0_ddlLocationType'))
        select.select_by_value(t)
        driver.execute_script("arguments[0].click();", butt)
        driver.implicitly_wait(5)
        time.sleep(3)
    
        while True:
            links = driver.find_elements_by_css_selector('div.listing-item-more-link')
            
            for l in links:
                link = l.find_element_by_css_selector('a').get_attribute('href')
                link_list.append([link, t])
            eles = driver.find_elements_by_css_selector('span.module-pg-no-link')
            
            if len(eles) == 2:
                if 'Next' in eles[0].text:
                    break

            nexts = driver.find_elements_by_css_selector('a#main_0_contentpanel_1_tablocationlisting_0_ucPagingTop_hlNext')

            if len(nexts) > 0:
                next_link = driver.find_elements_by_xpath('//a[contains(text(),"Next")]')[0].get_attribute('href')
                driver.get(next_link)
                driver.implicitly_wait(5)

            else:
                break    

    all_store_data = []
    for i, link in enumerate(link_list):
        page_url = link[0]
        location_type = link[1]
        driver.get(page_url)
        driver.implicitly_wait(5)
        
        location_name = driver.find_element_by_css_selector('h1').text

        addy_div = addy = driver.find_elements_by_css_selector('div#main_0_contentpanel_2_pnlAddress')
        if len(addy_div) > 0:
            addy = addy_div[0].text.split('\n')
        else:
            addy_div = driver.find_elements_by_css_selector('div#main_0_contentpanel_3_pnlAddress')
            if len(addy_div) > 0:
                addy = addy_div[0].text.split('\n')
            else:
                addy_div = driver.find_elements_by_css_selector('div#main_0_contentpanel_1_pnlAddress')
                if len(addy_div) > 0:
                    addy = addy_div[0].text.split('\n')
                else:
                    addy_div = driver.find_elements_by_css_selector('div#main_0_contentpanel_0_pnlAddress')
                    if len(addy_div) > 0:
                        addy = addy_div[0].text.split('\n')
                    else:
                        addy_div = driver.find_elements_by_css_selector('div#main_0_rightpanel_0_pnlAddress')
                        if len(addy_div) > 0:
                            addy = addy_div[0].text.split('\n')
                        else:
                            print('\n\n\n\n\n\n\n')
                            print('error')
                            print('\n\n\n\n\n\n\n')

        if len(addy) == 1:
            addy = ['1101 Madison St.', 'Seattle, WA 98104']

        if len(addy) == 3:
            street_address = addy[0]
            city, state, zip_code = addy_ext(addy[2])
        else:
            street_address = addy[0]
            city, state, zip_code = addy_ext(addy[1])
            
        phone_numbers = driver.find_element_by_css_selector('div.phones').find_elements_by_css_selector('a')

        if len(phone_numbers) > 0:
            phone_number = phone_numbers[0].text
        else:
            phone_number = '<MISSING>'
            
        hours_raw = driver.find_elements_by_css_selector('div.module-lc-hours')
        if len(hours_raw) == 1:
            hours_raw = hours_raw[0].text.replace('\n', ' ').replace('Office hours', '').strip()
        else:
            hours_raw = 'Monday-Friday, 9 a.m.-3 p.m.'

        if hours_raw == '':
            hours = '<MISSING>'
        else:
            hours = ' '.join(hours_raw.split())
        
        lat = '<MISSING>'
        longit = '<MISSING>'
        country_code = 'US'
        store_number = '<MISSING>'
        
        store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code, 
                    store_number, phone_number, location_type, lat, longit, hours, page_url]

        all_store_data.append(store_data)

    driver.quit()
    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
