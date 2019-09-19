import csv
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup

def get_driver():
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--window-size=1920,1080')
    return webdriver.Chrome('chromedriver', options=options)


def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    
    locator_domain = 'https://local.skechers.com/'

    driver = get_driver()
    driver.get(locator_domain)
    driver.implicitly_wait(10)


    main = driver.find_element_by_css_selector('div#content')

    state_hrefs = main.find_elements_by_css_selector('a.contentlist_item')
    state_links = []
    for state in state_hrefs:
        state_links.append(state.get_attribute('href'))


    link_list = []
    for link in state_links:
        driver.get(link)
        driver.implicitly_wait(10)
        main = driver.find_element_by_css_selector('div#content')

        loc_hrefs = main.find_elements_by_css_selector('a.contentlist_item')
        
        for loc in loc_hrefs:
            link_list.append(loc.get_attribute('href'))
        

    all_store_data = []
    
    for link in link_list:
        driver.get(link)
        driver.implicitly_wait(10)

        element = driver.find_element_by_css_selector('a.city_link')
        driver.execute_script("arguments[0].click();", element)
        driver.implicitly_wait(10)

        if 'Coming Soon' in driver.find_element_by_css_selector('div#storeinformation').text:
            continue

        xml = driver.find_element_by_css_selector('xml').get_attribute('innerHTML')

        xml_tree = BeautifulSoup(xml, features='lxml')
        
        poi = xml_tree.find('poi')
        location_name = poi.find('name').text + ' ' + poi.find('name2').text
        location_name = location_name.strip()
        street_address = poi.find('address1').text + ' ' + poi.find('address2').text
        street_address = street_address.strip()
        city = poi.find('city').text
        state = poi.find('state').text
        zip_code = poi.find('postalcode').text
        
        lat = poi.find('latitude').text
        longit = poi.find('longitude').text
        
        phone_number = poi.find('phone').text

        if phone_number == '':
            phone_number = '<MISSING>'

        if poi.find('rmon').text == '':
            hours = '<MISSING>'
        else:
            hours = 'Monday ' + poi.find('rmon').text + ' '
            hours += 'Tuesday ' + poi.find('rtues').text + ' '
            hours += 'Wednesday ' + poi.find('rwed').text + ' '
            hours += 'Thursday ' + poi.find('rthurs').text + ' '
            hours += 'Friday ' + poi.find('rfri').text + ' '
            hours += 'Saturday ' + poi.find('rsat').text + ' '
            hours += 'Sunday ' + poi.find('rsun').text
        
        location_type = poi.find('name').text.replace('SKECHERS', '').strip()
        
        
        store_number = '<MISSING>'
        country_code = 'US'


        store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code,
                     store_number, phone_number, location_type, lat, longit, hours ]



        all_store_data.append(store_data)
        

    driver.quit()
    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
